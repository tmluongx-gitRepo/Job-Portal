# Unified development environment with Node/Bun + Python
FROM node:20-bookworm

# Update SSL certificates first (separate step to ensure completion)
RUN apt-get update && apt-get install -y \
    ca-certificates \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install system dependencies
RUN apt-get update && \
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" > /etc/apt/sources.list.d/github-cli.list \
    && apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    vim \
    postgresql-client \
    redis-tools \
    gh \
    && rm -rf /var/lib/apt/lists/*

# Install Bun with verification (use direct download as fallback if curl fails)
RUN curl -fsSL https://bun.sh/install | bash || \
    (echo "Primary install failed, trying direct download..." && \
     apt-get update && apt-get install -y wget unzip && \
     mkdir -p /root/.bun/bin && \
     wget https://github.com/oven-sh/bun/releases/latest/download/bun-linux-x64.zip && \
     unzip bun-linux-x64.zip && \
     mv bun-linux-x64/bun /root/.bun/bin/bun && \
     chmod +x /root/.bun/bin/bun && \
     rm -rf bun-linux-x64.zip bun-linux-x64 && \
     apt-get remove -y wget unzip && apt-get autoremove -y) && \
    ls -la /root/.bun/bin/ && \
    /root/.bun/bin/bun --version && \
    ln -s /root/.bun/bin/bun /usr/local/bin/bun && \
    bun --version
ENV PATH="/root/.bun/bin:${PATH}"
ENV BUN_INSTALL="/root/.bun"

# Install Python package manager (uv for fast installs)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:${PATH}"

# Set working directory
WORKDIR /workspace

# Install global npm packages for development
RUN npm install -g typescript eslint prettier

# Disable npm to enforce bun usage
RUN mv /usr/local/bin/npm /usr/local/bin/npm-original && \
    echo '#!/bin/bash\necho "❌ ERROR: npm is disabled in this project!"\necho ""\necho "This project uses Bun as the package manager."\necho ""\necho "Please use:"\necho "  • bun install    (instead of npm install)"\necho "  • bun add        (instead of npm install <package>)"\necho "  • bun remove     (instead of npm uninstall)"\necho "  • bun run <cmd>  (instead of npm run <cmd>)"\necho ""\nexit 1' > /usr/local/bin/npm && \
    chmod +x /usr/local/bin/npm

# Disable pip to enforce uv usage
RUN mv /usr/bin/pip /usr/bin/pip-original && \
    mv /usr/bin/pip3 /usr/bin/pip3-original && \
    echo '#!/bin/bash\necho "❌ ERROR: pip is disabled in this project!"\necho ""\necho "This project uses UV as the Python package manager."\necho ""\necho "Please use:"\necho "  • uv pip install         (instead of pip install)"\necho "  • uv pip install <pkg>   (instead of pip install <package>)"\necho "  • uv pip uninstall       (instead of pip uninstall)"\necho "  • uv pip list            (instead of pip list)"\necho "  • uv pip freeze          (instead of pip freeze)"\necho ""\necho "For requirements.txt:"\necho "  • uv pip install -r requirements.txt"\necho ""\nexit 1' > /usr/bin/pip && \
    chmod +x /usr/bin/pip && \
    cp /usr/bin/pip /usr/bin/pip3

# Keep container running
CMD ["sleep", "infinity"]
