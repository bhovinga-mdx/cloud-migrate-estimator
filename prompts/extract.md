You are analyzing a sales call transcript for a cloud migration engagement.

Extract all information relevant to scoping and estimating a cloud migration project. Be thorough — anything not captured here is lost to downstream analysis.

Focus on:
- Current infrastructure (on-prem, cloud, hybrid, OS, databases, applications, networking, storage)
- Migration drivers and pain points
- Timeline and budget expectations or constraints
- Compliance and security requirements
- Workload details (count, data volumes, criticality, dependencies)
- Technical constraints or preferences
- Stakeholders mentioned

Rules:
- If information is ambiguous or contradictory, capture both interpretations in raw_notes.
- If information is missing, leave fields as null — do NOT infer or fabricate.
- Extract exact quotes where they convey important context (e.g., "we need to be off this by end of year").
- Capture implicit information (e.g., if they mention "our Oracle databases" that implies Oracle licensing costs).
