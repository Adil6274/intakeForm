import os
import secrets
import string
from datetime import datetime, date
from functools import wraps

from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, session, Response
)
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename

from config import Config

# -------------------------------------------------------------------
# App / extensions setup (single app instance)
# -------------------------------------------------------------------

app = Flask(__name__)
app.config.from_object(Config)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.jinja_env.auto_reload = True
app.config["UPLOAD_FOLDER"] = Config.UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = Config.MAX_CONTENT_LENGTH

mail = Mail(app)

db = SQLAlchemy(app)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf"}

# -------------------------------------------------------------------
# Admin auth
# -------------------------------------------------------------------

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "change_me_admin")


def check_admin_auth(username, password):
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD


def authenticate():
    return Response(
        "Admin login required.\n",
        401,
        {"WWW-Authenticate": 'Basic realm="Admin Dashboard"'}
    )


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_admin_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# -------------------------------------------------------------------
# Models
# -------------------------------------------------------------------


class Submission(db.Model):
    __tablename__ = "submissions"

    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(8), nullable=False, unique=True)
    full_name = db.Column(db.String(255))
    preferred_name = db.Column(db.String(255))
    profession = db.Column(db.String(255))
    tagline = db.Column(db.String(255))
    email = db.Column(db.String(255))
    phone = db.Column(db.String(100))
    whatsapp = db.Column(db.String(100))
    location = db.Column(db.String(255))
    time_zone = db.Column(db.String(255))
    bio_long = db.Column(db.Text)
    bio_short = db.Column(db.Text)
    company = db.Column(db.String(255))
    industry = db.Column(db.String(255))
    website_purpose = db.Column(db.String(255))
    target_audience = db.Column(db.Text)
    tone_style = db.Column(db.String(255))
    brand_keywords = db.Column(db.Text)
    color_prefs = db.Column(db.Text)
    dont_use_colors = db.Column(db.Text)
    inspiration = db.Column(db.Text)
    existing_website = db.Column(db.String(255))
    likes_existing = db.Column(db.Text)
    dislikes_existing = db.Column(db.Text)
    experience = db.Column(db.Text)
    education = db.Column(db.Text)
    skills = db.Column(db.Text)
    services_offered = db.Column(db.Text)
    achievements = db.Column(db.Text)
    primary_cta = db.Column(db.String(255))
    secondary_cta = db.Column(db.String(255))
    preferred_contact = db.Column(db.String(255))
    social_links = db.Column(db.JSON)
    projects = db.Column(db.JSON)
    pages = db.Column(db.JSON)
    features = db.Column(db.JSON)
    technical_prefs = db.Column(db.JSON)
    deadline = db.Column(db.Date)
    budget_range = db.Column(db.String(100))
    content_ready = db.Column(db.Text)
    other_notes = db.Column(db.Text)
    files = db.Column(db.JSON)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)


with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"Error creating database tables: {e}")
        print("Please check your database connection and credentials.")

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------


def generate_public_id(length: int = 8) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# -------------------------------------------------------------------
# Routes
# -------------------------------------------------------------------


@app.route("/", methods=["GET"])
def intake_form():
    return render_template("intake_form.html")


@app.route("/submit", methods=["POST"])
def submit():

    # Collect all form data
    form_data = {
        "full_name": request.form.get("fullName"),
        "preferred_name": request.form.get("preferredName"),
        "profession": request.form.get("profession"),
        "tagline": request.form.get("tagline"),
        "email": request.form.get("email"),
        "phone": request.form.get("phone"),
        "whatsapp": request.form.get("whatsapp"),
        "location": request.form.get("location"),
        "time_zone": request.form.get("timeZone"),
        "bio_long": request.form.get("bioLong"),
        "bio_short": request.form.get("bioShort"),
        "company": request.form.get("company"),
        "industry": request.form.get("industry"),
        "website_purpose": request.form.get("websitePurpose"),
        "target_audience": request.form.get("targetAudience"),
        "tone_style": request.form.get("toneStyle"),
        "brand_keywords": request.form.get("brandKeywords"),
        "color_prefs": request.form.get("colorPrefs"),
        "dont_use_colors": request.form.get("dontUseColors"),
        "inspiration": request.form.get("inspiration"),
        "existing_website": request.form.get("existingWebsite"),
        "likes_existing": request.form.get("likesExisting"),
        "dislikes_existing": request.form.get("dislikesExisting"),
        "experience": request.form.get("experience"),
        "education": request.form.get("education"),
        "skills": request.form.get("skills"),
        "services_offered": request.form.get("servicesOffered"),
        "achievements": request.form.get("achievements"),
        "primary_cta": request.form.get("primaryCta"),
        "secondary_cta": request.form.get("secondaryCta"),
        "preferred_contact": request.form.get("preferredContact"),
        "social_links": {
            "linkedin": request.form.get("linkedin"),
            "github": request.form.get("github"),
            "behance": request.form.get("behance"),
            "dribbble": request.form.get("dribbble"),
            "instagram": request.form.get("instagram"),
            "twitter": request.form.get("twitter"),
            "other": request.form.get("otherSocial"),
        },
        "projects_raw": {
            "titles": request.form.getlist("projectTitle[]"),
            "roles": request.form.getlist("projectRole[]"),
            "descs": request.form.getlist("projectDesc[]"),
            "tech": request.form.getlist("projectTech[]"),
            "results": request.form.getlist("projectResults[]"),
            "urls": request.form.getlist("projectUrl[]"),
        },
        "pages": request.form.getlist("pages[]"),
        "features": request.form.getlist("features[]"),
        "technical_prefs": {
            "cms": request.form.get("cmsPreference"),
            "blog": request.form.get("blogPreference"),
            "ongoingSupport": request.form.get("ongoingSupport"),
            "seo": request.form.get("seoLevel"),
            "analytics": request.form.get("analytics"),
        },
        "deadline_raw": request.form.get("deadline"),
        "budget_range": request.form.get("budgetRange"),
        "content_ready": request.form.get("contentReady"),
        "other_notes": request.form.get("otherNotes"),
    }

    # Handle file uploads
    uploaded_files = []
    for key in request.files:
        file = request.files[key]
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            ts_prefix = datetime.now().strftime("%Y%m%d_%H%M%S_")
            filename = ts_prefix + filename
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)
            uploaded_files.append(filename)

    form_data["uploaded_files"] = uploaded_files

    # Generate and store OTP in session
    otp = "".join(secrets.choice(string.digits) for _ in range(6))
    session["email_otp"] = otp
    session["email_otp_for"] = form_data["email"]
    session["pending_form"] = form_data
    session.modified = True


    # Send OTP email (no separate HTML file needed)
    try:
        subject = "Portfolio Intake – Email Verification"
        recipient = form_data["email"]

        plain_body = f"""Thank you for submitting your portfolio intake form!

Your verification code is: {otp}

Please enter this code on the verification page to complete your submission.
This code is valid for 10 minutes.

If you didn't request this, please ignore this email.
"""

        html_body = f"""
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>{subject}</title>
  </head>
  <body style="margin:0; padding:0; background-color:#0b1120; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
    <table role="presentation" cellspacing="0" cellpadding="0" border="0" align="center" width="100%" style="padding:24px 0;">
      <tr>
        <td align="center">
          <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="max-width:520px; background:#020617; border-radius:16px; border:1px solid #1f2937;">
            <tr>
              <td style="padding:24px 28px 18px 28px; text-align:left;">
                <div style="display:inline-flex; align-items:center; justify-content:center; width:36px; height:36px; border-radius:999px; background:linear-gradient(135deg,#38bdf8,#6366f1); margin-bottom:14px;">
                  <span style="font-size:18px; color:#0b1120; font-weight:600;">PB</span>
                </div>
                <h1 style="margin:0 0 8px 0; font-size:20px; font-weight:600; color:#e5e7eb;">
                  Verify your email
                </h1>
                <p style="margin:0; font-size:14px; line-height:1.6; color:#9ca3af;">
                  Thank you for submitting your portfolio intake form. To keep your details secure, we need to confirm that this email address belongs to you.
                </p>
              </td>
            </tr>
            <tr>
              <td style="padding:4px 28px 4px 28px;">
                <p style="margin:0 0 6px 0; font-size:13px; color:#9ca3af;">
                  Your verification code:
                </p>
                <div style="display:inline-block; padding:10px 18px; border-radius:12px; background:linear-gradient(135deg,#0f172a,#020617); border:1px solid rgba(148,163,184,0.5);">
                  <span style="font-family:Menlo,Consolas,monospace; font-size:22px; letter-spacing:0.3em; color:#f9fafb;">
                    {otp}
                  </span>
                </div>
                <p style="margin:10px 0 0 0; font-size:12px; color:#6b7280;">
                  This code is valid for <strong style="color:#e5e7eb;">10 minutes</strong>. Please enter it on the verification page to complete your submission.
                </p>
              </td>
            </tr>
            <tr>
              <td style="padding:18px 28px 10px 28px;">
                <p style="margin:0 0 4px 0; font-size:12px; color:#6b7280;">
                  If you didn’t request this, you can safely ignore this email.
                </p>
                <p style="margin:10px 0 0 0; font-size:12px; color:#4b5563;">
                  Best regards,<br/>
                  <span style="color:#e5e7eb;">Portfolio Builder</span>
                </p>
              </td>
            </tr>
            <tr>
              <td style="padding:10px 28px 20px 28px; border-top:1px solid #1f2937;">
                <p style="margin:0; font-size:11px; color:#4b5563;">
                  You’re receiving this email because someone submitted the portfolio intake form using this address.
                </p>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>
"""

        msg = Message(
            subject,
            sender=app.config.get("MAIL_DEFAULT_SENDER", "noreply@example.com"),
            recipients=[recipient],
        )
        msg.body = plain_body      # text fallback
        msg.html = html_body       # HTML version
        mail.send(msg)

        flash("Verification code sent to your email. Please check your inbox.", "info")
    except Exception as e:
        print(f"Email sending failed: {e}")
        if app.debug:
            flash(f"DEBUG: Your verification code is: {otp}", "warning")
            flash("Email sending failed, but proceeding with verification for testing.", "info")
        else:
            flash("Failed to send verification email. Please try again.", "danger")
        return redirect(url_for("intake_form"))

    return redirect(url_for("verify_email"))



@app.route("/verify-email", methods=["GET", "POST"])
def verify_email():
    
    # If there is no pending form in session, send user back
    if "pending_form" not in session or "email_otp" not in session or "email_otp_for" not in session:
        flash("No pending submission to verify.", "warning")
        return redirect(url_for("intake_form"))

    # GET: show the verify page
    if request.method == "GET":
        try:
            email_for = session.get("email_otp_for")
            return render_template("verify_email.html", email=email_for)
        except Exception as e:
            print(f"Template rendering error: {e}")
            return f"Template error: {e}"

    # POST: user submitted OTP
    user_otp = request.form.get("otp", "").strip()
    session_otp = session.get("email_otp")
    email_for = session.get("email_otp_for")
    form_data = session.get("pending_form")

    if not form_data or not session_otp or not email_for:
        flash("Verification session expired. Please submit the form again.", "warning")
        return redirect(url_for("intake_form"))

    if user_otp != session_otp:
        flash("Invalid verification code. Please try again.", "danger")
        return render_template("verify_email.html", email=email_for)

    # OTP correct → build projects and save Submission
    pr = form_data["projects_raw"]
    projects = []
    for i in range(len(pr["titles"])):
        title = pr["titles"][i].strip()
        if not title:
            continue
        projects.append(
            {
                "title": title,
                "role": pr["roles"][i],
                "description": pr["descs"][i],
                "tech": pr["tech"][i],
                "results": pr["results"][i],
                "url": pr["urls"][i],
            }
        )

    deadline = None
    if form_data.get("deadline_raw"):
        deadline = datetime.strptime(form_data["deadline_raw"], "%Y-%m-%d").date()

    submission = Submission(
        public_id=generate_public_id(),
        full_name=form_data["full_name"],
        preferred_name=form_data["preferred_name"],
        profession=form_data["profession"],
        tagline=form_data["tagline"],
        email=form_data["email"],
        phone=form_data["phone"],
        whatsapp=form_data["whatsapp"],
        location=form_data["location"],
        time_zone=form_data["time_zone"],
        bio_long=form_data["bio_long"],
        bio_short=form_data["bio_short"],
        company=form_data["company"],
        industry=form_data["industry"],
        website_purpose=form_data["website_purpose"],
        target_audience=form_data["target_audience"],
        tone_style=form_data["tone_style"],
        brand_keywords=form_data["brand_keywords"],
        color_prefs=form_data["color_prefs"],
        dont_use_colors=form_data["dont_use_colors"],
        inspiration=form_data["inspiration"],
        existing_website=form_data["existing_website"],
        likes_existing=form_data["likes_existing"],
        dislikes_existing=form_data["dislikes_existing"],
        experience=form_data["experience"],
        education=form_data["education"],
        skills=form_data["skills"],
        services_offered=form_data["services_offered"],
        achievements=form_data["achievements"],
        primary_cta=form_data["primary_cta"],
        secondary_cta=form_data["secondary_cta"],
        preferred_contact=form_data["preferred_contact"],
        social_links=form_data["social_links"],
        projects=projects,
        pages=form_data["pages"],
        features=form_data["features"],
        technical_prefs=form_data["technical_prefs"],
        deadline=deadline,
        budget_range=form_data["budget_range"],
        content_ready=form_data["content_ready"],
        other_notes=form_data["other_notes"],
        files=form_data.get("uploaded_files", []),
    )

    try:
        db.session.add(submission)
        db.session.commit()

        # Clear OTP and pending data from session
        session.pop("pending_form", None)
        session.pop("email_otp", None)
        session.pop("email_otp_for", None)

        flash("Email verified and form submitted successfully!", "success")
        return redirect(url_for("thank_you", public_id=submission.public_id))
    except Exception as e:
        db.session.rollback()
        flash(f"Error saving submission: {e}", "danger")
        return redirect(url_for("intake_form"))

@app.route("/thank-you/<public_id>")
def thank_you(public_id):
    return render_template("thank_you.html", public_id=public_id)


@app.route("/admin/submissions")
@admin_required
def admin_submissions():
    submissions = Submission.query.order_by(Submission.submitted_at.desc()).all()
    today = datetime.combine(date.today(), datetime.min.time())
    return render_template("admin_submissions.html", submissions=submissions, today=today)


@app.route("/admin/submission/<public_id>")
@admin_required
def admin_submission_detail(public_id):
    submission = Submission.query.filter_by(public_id=public_id).first()
    if not submission:
        return "Submission not found", 404
    return render_template("admin_submission_detail.html", submission=submission)


@app.route("/intake-pdf/<public_id>")
def intake_pdf(public_id):
    submission = Submission.query.filter_by(public_id=public_id).first()
    if not submission:
        print(f"Submission not found for public_id: {public_id}")
        return "Not found", 404

    print(f"Found submission: {submission.full_name}, {submission.public_id}")
    data = {
        "fullName": submission.full_name,
        "preferredName": submission.preferred_name,
        "profession": submission.profession,
        "tagline": submission.tagline,
        "email": submission.email,
        "phone": submission.phone,
        "whatsapp": submission.whatsapp,
        "location": submission.location,
        "timeZone": submission.time_zone,
        "bioShort": submission.bio_short,
        "bioLong": submission.bio_long,
        "company": submission.company,
        "industry": submission.industry,
        "websitePurpose": submission.website_purpose,
        "targetAudience": submission.target_audience,
        "toneStyle": submission.tone_style,
        "brandKeywords": submission.brand_keywords,
        "colorPrefs": submission.color_prefs,
        "dontUseColors": submission.dont_use_colors,
        "inspiration": submission.inspiration,
        "existingWebsite": submission.existing_website,
        "likesExisting": submission.likes_existing,
        "dislikesExisting": submission.dislikes_existing,
        "experience": submission.experience,
        "education": submission.education,
        "skills": submission.skills,
        "servicesOffered": submission.services_offered,
        "achievements": submission.achievements,
        "primaryCta": submission.primary_cta,
        "secondaryCta": submission.secondary_cta,
        "preferredContact": submission.preferred_contact,
        "socialLinks": submission.social_links,
        "projects": submission.projects,
        "pages": submission.pages,
        "features": submission.features,
        "technicalPrefs": submission.technical_prefs,
        "deadline": submission.deadline.strftime("%Y-%m-%d") if submission.deadline else None,
        "budgetRange": submission.budget_range,
        "contentReady": submission.content_ready,
        "otherNotes": submission.other_notes,
    }
    generated_on = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    qr_url = "https://via.placeholder.com/120x120?text=QR+Code"
    return render_template(
        "intake_pdf.html",
        public_id=public_id,
        data=data,
        generated_on=generated_on,
        qr_url=qr_url,
    )


print("Registered routes:", [rule.rule for rule in app.url_map.iter_rules()])

if __name__ == "__main__":
    app.run(debug=True, port=5001)
