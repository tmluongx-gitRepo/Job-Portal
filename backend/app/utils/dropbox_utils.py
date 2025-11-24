"""
Dropbox service for file storage operations.
"""

from datetime import UTC, datetime

import dropbox
from dropbox.exceptions import ApiError, AuthError
from dropbox.files import WriteMode

from app.config import settings


class DropboxService:
    """Service for interacting with Dropbox API."""

    def __init__(self) -> None:
        """Initialize Dropbox client with app credentials."""
        if not settings.DROPBOX_ACCESS_TOKEN:
            raise ValueError(
                "Dropbox access token not configured. "
                "Please set DROPBOX_ACCESS_TOKEN in your .env file. "
                "See docs/DROPBOX_SETUP.md for instructions."
            )

        self.access_token = settings.DROPBOX_ACCESS_TOKEN
        self.client: dropbox.Dropbox | None = None

    def _get_client(self) -> dropbox.Dropbox:
        """Get or create Dropbox client."""
        if self.client is None:
            try:
                self.client = dropbox.Dropbox(self.access_token)
            except Exception as e:
                raise ValueError(f"Failed to initialize Dropbox client: {e}") from e
        return self.client

    def upload_file(self, file_content: bytes, user_id: str) -> str:
        """
        Upload a resume file to Dropbox.

        Args:
            file_content: File content as bytes
            user_id: User ID for file naming

        Returns:
            Dropbox path where file was uploaded

        Raises:
            ApiError: If upload fails
        """
        dropbox_path = f"/resumes/{user_id}.pdf"

        try:
            client = self._get_client()
            # Upload file, overwriting if it exists
            client.files_upload(
                file_content, dropbox_path, mode=WriteMode("overwrite"), autorename=False
            )
        except AuthError as e:
            raise ValueError(f"Dropbox authentication failed: {e}") from e
        except ApiError as e:
            raise ValueError(f"Dropbox upload failed: {e}") from e
        else:
            return dropbox_path

    def download_file(self, dropbox_path: str) -> bytes:
        """
        Download a file from Dropbox.

        Args:
            dropbox_path: Path to file in Dropbox

        Returns:
            File content as bytes

        Raises:
            ApiError: If download fails
        """
        try:
            client = self._get_client()
            _metadata, response = client.files_download(dropbox_path)
        except AuthError as e:
            raise ValueError(f"Dropbox authentication failed: {e}") from e
        except ApiError as e:
            if e.error.is_path() and e.error.get_path().is_not_found():
                raise FileNotFoundError(f"File not found: {dropbox_path}") from e
            raise ValueError(f"Dropbox download failed: {e}") from e
        else:
            return response.content  # type: ignore[no-any-return]

    def delete_file(self, dropbox_path: str) -> bool:
        """
        Delete a file from Dropbox.

        Args:
            dropbox_path: Path to file in Dropbox

        Returns:
            True if deleted successfully

        Raises:
            ApiError: If deletion fails
        """
        try:
            client = self._get_client()
            client.files_delete_v2(dropbox_path)
        except AuthError as e:
            raise ValueError(f"Dropbox authentication failed: {e}") from e
        except ApiError as e:
            if e.error.is_path_lookup() and e.error.get_path_lookup().is_not_found():
                # File doesn't exist, consider it deleted
                return True
            raise ValueError(f"Dropbox deletion failed: {e}") from e
        else:
            return True

    def get_file_metadata(self, dropbox_path: str) -> dict | None:
        """
        Get metadata for a file in Dropbox.

        Args:
            dropbox_path: Path to file in Dropbox

        Returns:
            Metadata dict or None if file doesn't exist
        """
        try:
            client = self._get_client()
            metadata = client.files_get_metadata(dropbox_path)
            return {
                "path": metadata.path_display,
                "size": getattr(metadata, "size", 0),
                "modified": getattr(metadata, "server_modified", datetime.now(UTC)),
            }
        except AuthError as e:
            raise ValueError(f"Dropbox authentication failed: {e}") from e
        except ApiError as e:
            if e.error.is_path() and e.error.get_path().is_not_found():
                return None
            raise ValueError(f"Dropbox metadata fetch failed: {e}") from e


# Singleton instance
_dropbox_service: DropboxService | None = None


def get_dropbox_service() -> DropboxService:
    """Get singleton Dropbox service instance."""
    global _dropbox_service
    if _dropbox_service is None:
        _dropbox_service = DropboxService()
    return _dropbox_service
