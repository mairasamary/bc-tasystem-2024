"""
Help tab content derived from existing site workflows.

The same article catalog powers:
- role-aware Help landing pages
- role-aware search results
- individual article pages
- the student printable guide
"""

HELP_TOPICS = [
    {
        "audience": "student",
        "id": "getting-started",
        "title": "Getting started (Welcome + Profile)",
        "category": "Getting started",
        "summary": "Create your TA Connect student profile so you can browse courses and submit applications.",
        "screenshot_static_path": "images/help/getting-started.png",
        "screenshot_alt": "Example: Getting started (Student profile page)",
        "screenshot_caption": "Example screenshot: Getting started",
        "prerequisites": [
            "You are a student (not a professor/admin).",
            "If you just joined, you may need to complete the one-time welcome flow first.",
        ],
        "steps": [
            "Open the `Welcome` page (`/welcome/`) if you see it.",
            "In `Welcome`, acknowledge whether you were previously a Boston College student worker (TA or other student job), then click `Get started`.",
            "Complete the `Profile` page (`/profile/`): enter your 8-digit Eagle ID, choose your Graduation Year, and upload your resume (PDF/DOC/DOCX).",
            "Add (optional) CV, skills, and past course info, then click `Save profile`.",
            "After your profile is complete, your ability to apply shows up on the `Courses` page."
        ],
        "what_to_know": [
            "Student access is gated by your profile completion for applying.",
            "Your profile completion for applying requires: a valid 8-digit Eagle ID, a Graduation Year, and an uploaded resume."
        ],
        "troubleshooting": [
            "If you are redirected away from other pages, it usually means your welcome/profile is not complete yet. Check `/welcome/` and `/profile/`."
        ],
    },
    {
        "audience": "student",
        "id": "apply-to-course",
        "title": "Apply to a course (TA position)",
        "category": "Applications",
        "summary": "Submit an application to a course, answer any required custom questions, and send your resume snapshot for review.",
        "screenshot_static_path": "images/help/apply-to-course.png",
        "screenshot_alt": "Example: Apply to a course workflow (Apply form page)",
        "screenshot_caption": "Example screenshot: Apply to a course",
        "prerequisites": [
            "The course must be open to applications (course status is not closed).",
            "You must be a student and not already assigned as a TA for a course.",
            "You cannot already have an application to the same course.",
            "Your profile must be complete for applying.",
            "You must be under the per-term application limit (5 counted applications per term).",
        ],
        "steps": [
            "Go to `Courses` (`/courses/`) and use search/filter to find the right course and term.",
            "On a course you want, click `Apply` (the button appears only when you are allowed to apply).",
            "Complete the application form:",
            "Answer required custom questions for that course.",
            "Provide any additional text required by the form.",
            "Submit the form.",
            "After submission, your application is created with status `PENDING`, and your application includes snapshots of your resume/photo/skills at submission time."
        ],
        "what_to_know": [
            "The site enforces the per-term limit by counting application statuses `PENDING`, `ACCEPTED`, and `CONFIRMED` for the current term. `REJECTED` and `WITHDRAWN` do not count toward the limit.",
            "If the professor sends an offer, your application status will advance to `ACCEPTED`, and you will later confirm via offer acceptance."
        ],
        "troubleshooting": [
            "If applying fails with profile-related errors: add the missing fields on `/profile/` (Eagle ID, Graduation Year, resume).",
            "If you see an error saying the course is closed: choose another course; closed courses cannot accept applications.",
            "If you see the 5-application limit message: withdraw old applications (if allowed) or wait for the next term."
        ],
    },
    {
        "audience": "student",
        "id": "edit-withdraw-application",
        "title": "Edit or withdraw an application",
        "category": "Applications",
        "summary": "Update your application answers while it is still `PENDING` or `ACCEPTED`, or withdraw when allowed.",
        "screenshot_static_path": "images/help/edit-withdraw-application.png",
        "screenshot_alt": "Example: Edit or withdraw an application (Application details page)",
        "screenshot_caption": "Example screenshot: Edit/withdraw application",
        "prerequisites": [
            "You can only edit/withdraw your own applications.",
            "Only applications in status `PENDING` or `ACCEPTED` can be edited.",
            "Only applications in status `PENDING` or `ACCEPTED` can be withdrawn."
        ],
        "steps": [
            "Open your application from the `Applications` page (`/applications/`).",
            "To edit: submit changes via the application `Edit` action (updates your additional info, custom question answers, and your snapshot fields).",
            "To withdraw: use the application `Withdraw` action.",
            "Withdraw requires a POST action (so it is not safe to change via the browser address bar); use the UI button/link."
        ],
        "what_to_know": [
            "After withdrawing, your application status becomes `WITHDRAWN` and the course professor is notified.",
            "After editing, your application snapshot fields are updated from your current profile."
        ],
        "troubleshooting": [
            "If edit/withdraw is blocked, your application likely moved past `PENDING`/`ACCEPTED`. Use the status to decide whether you should wait, or respond to an offer instead."
        ],
    },
    {
        "audience": "student",
        "id": "respond-to-offers",
        "title": "Respond to TA offers (Accept or Decline)",
        "category": "Offers",
        "summary": "When you receive an offer, accept to be assigned as a TA, or decline to reject it.",
        "screenshot_static_path": "images/help/respond-to-offers.png",
        "screenshot_alt": "Example: Respond to TA offers (Offers page)",
        "screenshot_caption": "Example screenshot: Respond to offers",
        "prerequisites": [
            "You must have an offer available on your `Offers` page (`/offers/`).",
            "Accept/decline actions are for the offer recipient (you).",
        ],
        "steps": [
            "Open `Offers` (`/offers/`) and find your pending offer(s).",
            "To accept: use the accept action for that offer.",
            "To decline: use the decline action for that offer.",
        ],
        "what_to_know": [
            "Accepting an offer confirms your linked application (application status becomes `CONFIRMED`).",
            "Accepting also withdraws your other applications in statuses `PENDING`/`ACCEPTED` (sets them to `WITHDRAWN`) and rejects other pending offers.",
            "Once accepted, you are assigned as a TA for the course, and your other TA assignments are adjusted so you have at most one TA position.",
            "Declining an offer rejects the offer and marks the linked application as `REJECTED`."
        ],
        "troubleshooting": [
            "If you cannot accept because you are already a TA elsewhere: the site blocks a second active assignment. Review your currently assigned TA course and any pending offers."
        ],
    },
    {
        "audience": "student",
        "id": "employment-onboarding",
        "title": "Complete the student employment onboarding checklist",
        "category": "Onboarding",
        "summary": "After you accept a TA offer, record which BC onboarding forms you completed.",
        "screenshot_static_path": "images/help/employment-onboarding.png",
        "screenshot_alt": "Example: Student employment onboarding checklist page",
        "screenshot_caption": "Example screenshot: Employment onboarding checklist",
        "prerequisites": [
            "You must have a TA assignment for at least one course.",
            "If your onboarding checklist is already marked complete, you will be redirected back to your dashboard."
        ],
        "steps": [
            "Open `Student employment onboarding` (`/employment-onboarding/`).",
            "Check each item when you have completed it:",
            "Required Onboarding Form",
            "I-9",
            "Payroll Form Statement (Student Hours)",
            "W-4",
            "M-4",
            "Direct Deposit Enrollment Instructions",
            "Click `Save checklist`.",
            "After saving, return to your dashboard (or refresh to see updates)."
        ],
        "what_to_know": [
            "This checklist is for your own tracking. Official onboarding is managed outside the app (the page links to the Office of Student Services).",
            "The app uses these checkboxes to determine whether `onboarding_complete` is true."
        ],
        "troubleshooting": [
            "If you get redirected: you likely do not have a TA assignment yet. Accept an offer first."
        ],
    },
    {
        "audience": "professor",
        "id": "professor-dashboard-and-staffing",
        "title": "Use the professor dashboard and staffing overview",
        "category": "Dashboard",
        "summary": "Track your active courses, understaffed sections, pending applications, and pending offers from one dashboard.",
        "screenshot_static_path": "images/help/professor-dashboard-and-staffing.png",
        "screenshot_alt": "Professor dashboard and staffing overview",
        "screenshot_caption": "Example screenshot: Professor dashboard and staffing overview",
        "prerequisites": [
            "You must be signed in as a professor.",
            "You should already have one or more courses assigned to you to see staffing data."
        ],
        "steps": [
            "Open `Dashboard` (`/dashboard/`).",
            "Review the stat cards for active courses, understaffed courses, pending applications, and pending offers.",
            "Use the `Course Staffing Overview` table to inspect TA staffing, pending applications, and pending offers per course.",
            "Use the `Manage` action for a course when you need to edit details or review staffing more closely."
        ],
        "what_to_know": [
            "The dashboard is professor-specific and only shows your assigned courses.",
            "Understaffed counts are based on current TA assignments compared with required TA slots."
        ],
        "troubleshooting": [
            "If you see no courses, ask an admin to assign courses to your professor account."
        ],
    },
    {
        "audience": "professor",
        "id": "review-applications-and-send-offers",
        "title": "Review applications and send offers",
        "category": "Hiring",
        "summary": "Review student applications for your courses, inspect answers and profile snapshots, and send offers when capacity allows.",
        "screenshot_static_path": "images/help/review-applications-and-send-offers.png",
        "screenshot_alt": "Professor reviewing an application and sending offers",
        "screenshot_caption": "Example screenshot: Review applications and send offers",
        "prerequisites": [
            "You must be the assigned professor for the course, or an admin.",
            "The application must still be `PENDING` before an offer can be sent."
        ],
        "steps": [
            "Open `Applications` (`/applications/`) to see applications for your courses.",
            "Select an application to open `Application Details`.",
            "Review the student's profile snapshot, resume, skills, past courses, and custom-question answers.",
            "If you want to hire the student and there is TA offer capacity, click `Make offer`.",
            "If the application is not a fit, use `Reject` instead."
        ],
        "what_to_know": [
            "Sending an offer changes the application status from `PENDING` to `ACCEPTED` (offer sent).",
            "You cannot send more pending/filled offers than the course's TA slot capacity.",
            "Students receive notifications and email when an offer is sent."
        ],
        "troubleshooting": [
            "If `Make offer` is unavailable, the course may already have all TA offer slots in use.",
            "If you cannot open an application, verify the course belongs to you."
        ],
    },
    {
        "audience": "professor",
        "id": "manage-course-details-and-questions",
        "title": "Manage course details, TAs, and custom application questions",
        "category": "Courses",
        "summary": "View course details, manage assigned TAs, and add or remove custom questions students must answer during application.",
        "screenshot_static_path": "images/help/manage-course-details-and-questions.png",
        "screenshot_alt": "Professor managing course details and custom questions",
        "screenshot_caption": "Example screenshot: Manage course details and questions",
        "prerequisites": [
            "You must be the professor assigned to the course, or an admin."
        ],
        "steps": [
            "Open `Courses` and select one of your courses.",
            "Review the course details such as room, timeslot, TA count, and description.",
            "Use the `Application questions` section to add custom questions for applicants.",
            "Use the `Current TAs` section to review assigned students and remove a TA if needed."
        ],
        "what_to_know": [
            "You can add up to 5 custom questions per course.",
            "Questions with existing student answers cannot be deleted.",
            "Removing a TA reverts the student's accepted offer/application state and reopens the course if a slot becomes available."
        ],
        "troubleshooting": [
            "If you cannot manage questions or remove a TA, make sure you are the course professor and not viewing another professor's course."
        ],
    },
    {
        "audience": "professor",
        "id": "track-offers-and-ta-evaluations",
        "title": "Track offers and submit TA evaluations",
        "category": "Follow-up",
        "summary": "Monitor offer responses and complete TA evaluations for your assigned TAs.",
        "screenshot_static_path": "images/help/track-offers-and-ta-evaluations.png",
        "screenshot_alt": "Professor tracking offers and TA evaluations",
        "screenshot_caption": "Example screenshot: Track offers and TA evaluations",
        "prerequisites": [
            "You must be signed in as a professor.",
            "TA evaluations apply to TAs connected to your courses."
        ],
        "steps": [
            "Open `Offers` (`/offers/`) to see offers you have sent and whether students accepted or declined them.",
            "Use `Application Details` from the offers list if you need to revisit the applicant record.",
            "Open `Evaluations` (`/evaluations/`) to view existing evaluations or create a new one.",
            "Search by TA name in the evaluations page if you need to review prior feedback."
        ],
        "what_to_know": [
            "Pending offers remain open until the student accepts or declines.",
            "Accepted offers result in confirmed TA assignments.",
            "Evaluations are part of the course staffing lifecycle and are especially relevant after a semester closes."
        ],
        "troubleshooting": [
            "If there are no evaluations listed, you may not have submitted any yet or there may be no eligible TAs to review."
        ],
    },
    {
        "audience": "admin",
        "id": "admin-dashboard-and-system-overview",
        "title": "Use the admin dashboard and system overview",
        "category": "Dashboard",
        "summary": "Monitor the full TA system with platform-wide stats, recent applications, and recent offers.",
        "screenshot_static_path": "images/help/admin-dashboard-and-system-overview.png",
        "screenshot_alt": "Admin dashboard and system overview",
        "screenshot_caption": "Example screenshot: Admin dashboard and system overview",
        "prerequisites": [
            "You must be signed in as an admin/superuser."
        ],
        "steps": [
            "Open `Dashboard` (`/dashboard/`).",
            "Review the platform-wide stat cards for pending applications, total offers, active courses, and total users.",
            "Use the recent applications and recent offers tables to jump into detailed records."
        ],
        "what_to_know": [
            "Unlike professors, admins see system-wide data rather than course-specific data.",
            "The dashboard is a quick monitoring surface, not the only place to manage records."
        ],
        "troubleshooting": [
            "If a table appears empty, verify that the current environment has seeded or live data."
        ],
    },
    {
        "audience": "admin",
        "id": "create-edit-and-upload-courses",
        "title": "Create, edit, and upload courses",
        "category": "Courses",
        "summary": "Add courses manually, edit existing ones, or bulk-upload courses from an Excel spreadsheet.",
        "screenshot_static_path": "images/help/create-edit-and-upload-courses.png",
        "screenshot_alt": "Admin course management tools",
        "screenshot_caption": "Example screenshot: Create, edit, and upload courses",
        "prerequisites": [
            "You must be signed in as an admin/superuser."
        ],
        "steps": [
            "Open `Courses` (`/courses/`) to browse the current catalog.",
            "Use `Create Course` to add a course manually.",
            "Open a course and choose `Manage course` or edit it from the courses list when changes are needed.",
            "Use `Upload Courses` to import courses from an Excel spreadsheet when bulk updates are easier."
        ],
        "what_to_know": [
            "Admins can assign professors, edit course capacity, update course descriptions, and delete courses.",
            "Deleting a course also removes associated applications and offers."
        ],
        "troubleshooting": [
            "If an upload fails, confirm the spreadsheet uses the expected columns shown on the upload page."
        ],
    },
    {
        "audience": "admin",
        "id": "manage-onboarding-status-and-reminders",
        "title": "Manage onboarding status and reminders",
        "category": "Onboarding",
        "summary": "Track TA onboarding completion across the system, export records, and send reminder emails to incomplete TAs.",
        "screenshot_static_path": "images/help/manage-onboarding-status-and-reminders.png",
        "screenshot_alt": "Admin onboarding status and reminders page",
        "screenshot_caption": "Example screenshot: Manage onboarding status and reminders",
        "prerequisites": [
            "You must be signed in as an admin/superuser.",
            "Students must already be assigned as TAs for onboarding status to appear."
        ],
        "steps": [
            "Open `Onboarding Status` (`/onboarding-status/`).",
            "Review the summary cards for total, complete, and incomplete onboarding counts.",
            "Use the status table to inspect form-by-form progress for each TA.",
            "Click `Email incomplete TAs` to send reminder emails.",
            "Use `Export to Excel` if you need an offline copy."
        ],
        "what_to_know": [
            "This view is intended for admin oversight of student employment onboarding.",
            "Progress is based on the self-reported onboarding checklist students complete in the app."
        ],
        "troubleshooting": [
            "If the table is empty, no TAs may currently be assigned."
        ],
    },
    {
        "audience": "admin",
        "id": "export-schedule-and-close-semester",
        "title": "Export schedules and close the semester",
        "category": "Operations",
        "summary": "Download course schedules and perform semester-close actions that wrap up staffing and evaluations.",
        "screenshot_static_path": "images/help/export-schedule-and-close-semester.png",
        "screenshot_alt": "Admin schedule export and close semester controls",
        "screenshot_caption": "Example screenshot: Export schedules and close the semester",
        "prerequisites": [
            "You must be signed in as an admin/superuser."
        ],
        "steps": [
            "Open `Courses` to export the current filtered schedule if needed.",
            "Use `Export Schedule` to download the course data as an Excel file.",
            "Open `Upload Courses` when you need the semester-close controls.",
            "Use `Close Semester` to mark courses inactive and trigger the TA evaluation follow-up flow."
        ],
        "what_to_know": [
            "Closing the semester is a high-impact operational step and is not easily undone.",
            "Exported schedule files reflect the current filters and staffing state."
        ],
        "troubleshooting": [
            "Before closing the semester, confirm the course list and staffing records are accurate."
        ],
    },
]

