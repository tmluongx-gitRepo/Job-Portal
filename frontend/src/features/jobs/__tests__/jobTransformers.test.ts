/**
 * Tests for job transformer functions
 */
import { formatSalary, transformJobForUI } from "../utils/jobTransformers";
import type { Job as ApiJob } from "@/lib/api";

describe("formatSalary", () => {
  it("should format salary range", () => {
    expect(formatSalary(50000, 70000)).toBe("$50,000 - $70,000");
  });

  it("should format minimum salary only", () => {
    expect(formatSalary(50000)).toBe("$50,000+");
  });

  it("should return null if no salary provided", () => {
    expect(formatSalary()).toBeNull();
  });
});

describe("transformJobForUI", () => {
  it("should transform API job to UI format", () => {
    const apiJob: ApiJob = {
      id: "123",
      title: "Software Engineer",
      company: "Tech Corp",
      description: "Great job",
      location: "San Francisco",
      job_type: "Full-time",
      remote_ok: true,
      salary_min: 100000,
      salary_max: 150000,
      skills_required: ["TypeScript", "React"],
      responsibilities: ["Build features"],
      benefits: ["Health insurance"],
      is_active: true,
      view_count: 10,
      application_count: 5,
      created_at: new Date("2024-01-01"),
      updated_at: new Date("2024-01-01"),
    };

    const uiJob = transformJobForUI(apiJob);

    expect(uiJob.id).toBe("123");
    expect(uiJob.title).toBe("Software Engineer");
    expect(uiJob.company).toBe("Tech Corp");
    expect(uiJob.salary).toBe("$100,000 - $150,000");
    expect(uiJob.requirements).toEqual(["TypeScript", "React"]);
    expect(uiJob.benefits).toEqual(["Health insurance"]);
  });
});
