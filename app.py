import streamlit as st
from groq import Groq
from fpdf import FPDF
import tempfile
import os

# ─── Page Config ───────────────────────────────────────────────
st.set_page_config(
    page_title="MaSu.in - AI Resume Builder",
    page_icon="🦚",
    layout="wide"
)

# ─── Groq Client ───────────────────────────────────────────────
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ─── Session State ─────────────────────────────────────────────
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True
if 'resume' not in st.session_state:
    st.session_state.resume = None

# ─── Morpankh SVG ──────────────────────────────────────────────
MORPANKH = """<svg style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:280px;height:280px;opacity:0.15;pointer-events:none;z-index:0;" viewBox="0 0 300 300" xmlns="http://www.w3.org/2000/svg">
  <line x1="150" y1="290" x2="150" y2="160" stroke="#4a9e6a" stroke-width="3"/>
  <path d="M150,260 Q130,220 90,170" fill="none" stroke="#4a9e6a" stroke-width="1.5"/>
  <path d="M150,255 Q125,210 75,155" fill="none" stroke="#5ab07a" stroke-width="1.3"/>
  <path d="M150,248 Q120,200 60,140" fill="none" stroke="#6ec48e" stroke-width="1.1"/>
  <path d="M150,240 Q115,190 48,128" fill="none" stroke="#86c59f" stroke-width="0.9"/>
  <path d="M150,260 Q170,220 210,170" fill="none" stroke="#4a9e6a" stroke-width="1.5"/>
  <path d="M150,255 Q175,210 225,155" fill="none" stroke="#5ab07a" stroke-width="1.3"/>
  <path d="M150,248 Q180,200 240,140" fill="none" stroke="#6ec48e" stroke-width="1.1"/>
  <path d="M150,240 Q185,190 252,128" fill="none" stroke="#86c59f" stroke-width="0.9"/>
  <path d="M90,170 Q95,160 105,158" fill="none" stroke="#4a9e6a" stroke-width="0.8"/>
  <path d="M90,170 Q95,178 105,180" fill="none" stroke="#4a9e6a" stroke-width="0.8"/>
  <path d="M210,170 Q205,160 195,158" fill="none" stroke="#4a9e6a" stroke-width="0.8"/>
  <path d="M210,170 Q205,178 195,180" fill="none" stroke="#4a9e6a" stroke-width="0.8"/>
  <ellipse cx="150" cy="118" rx="38" ry="46" fill="none" stroke="#7c4daa" stroke-width="1.5"/>
  <ellipse cx="150" cy="118" rx="26" ry="32" fill="none" stroke="#4a9e6a" stroke-width="1.5"/>
  <ellipse cx="150" cy="118" rx="16" ry="20" fill="#2d5a8e" opacity="0.5"/>
  <ellipse cx="150" cy="118" rx="9" ry="11" fill="#1a3a6e" opacity="0.6"/>
  <ellipse cx="150" cy="118" rx="5" ry="6" fill="#f5c842" opacity="0.5"/>
  <path d="M150,72 Q145,60 150,50 Q155,60 150,72" fill="#f5c842" opacity="0.6"/>
  <circle cx="150" cy="48" r="4" fill="#f5c842" opacity="0.5"/>
</svg>"""

# ─── Theme Colors ──────────────────────────────────────────────
if st.session_state.dark_mode:
    BG1="#1a0533"; BG2="#12022a"; BG3="#0d0220"; BGI="#1e0442"
    T1="#f5c842";  T2="#c084fc";  T3="rgba(192,132,252,0.45)"
    BR="rgba(245,200,66,0.22)";   SC="#f5c842"; IC="rgba(245,200,66,0.12)"
else:
    BG1="#ffffff"; BG2="#f0faf4"; BG3="#f7f3ff"; BGI="#f9fff9"
    T1="#2d5a3d";  T2="#7c4daa";  T3="rgba(124,77,170,0.45)"
    BR="rgba(100,180,130,0.28)";  SC="#4a8f62"; IC="rgba(100,180,130,0.13)"

# ─── CSS ───────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600&family=Lato:wght@300;400;700&display=swap');
#MainMenu,footer,header{{visibility:hidden;}}
.block-container{{padding:0!important;max-width:100%!important;}}
[data-testid="stAppViewContainer"]{{background:{BG3}!important;}}
[data-testid="stHeader"]{{background:transparent!important;}}
.topbar{{background:{BG1};padding:13px 20px;display:flex;align-items:center;justify-content:space-between;border-bottom:0.5px solid {BR};}}
.logo-name{{font-family:'Cinzel',serif;font-size:18px;color:{T1};letter-spacing:1px;}}
.logo-sub{{font-size:10px;color:{T2};letter-spacing:2px;}}
.logo-icon{{width:36px;height:36px;border-radius:50%;background:{IC};border:1.5px solid {SC};display:flex;align-items:center;justify-content:center;font-size:16px;}}
.hero{{background:{BG1};padding:16px 20px;text-align:center;border-bottom:0.5px solid {BR};}}
.hero h2{{font-family:'Cinzel',serif;font-size:18px;color:{T1};margin-bottom:4px;}}
.hero p{{font-size:12px;color:{T2};margin-bottom:10px;}}
.steps-row{{display:flex;justify-content:center;gap:8px;flex-wrap:wrap;}}
.step-pill{{background:{IC};border:0.5px solid {SC};border-radius:20px;padding:3px 12px;font-size:11px;color:{T1};display:inline-block;}}
.sec-title{{font-family:'Cinzel',serif;font-size:11px;font-weight:600;color:{SC};letter-spacing:2px;margin-bottom:8px;margin-top:8px;}}
.stTextInput>div>div>input,.stTextArea>div>div>textarea{{background:{BGI}!important;border:0.5px solid {BR}!important;color:{T1}!important;border-radius:6px!important;font-family:'Lato',sans-serif!important;}}
.stTextInput label,.stTextArea label{{color:{T2}!important;font-size:12px!important;}}
.stCheckbox label{{color:{T2}!important;font-size:12px!important;}}
.stButton>button{{background:{IC}!important;border:1px solid {SC}!important;color:{T1}!important;font-family:'Cinzel',serif!important;font-size:13px!important;border-radius:8px!important;width:100%!important;padding:0.75rem!important;letter-spacing:1px!important;}}
.stDownloadButton>button{{background:transparent!important;border:1px solid {SC}!important;color:{T1}!important;width:100%!important;border-radius:8px!important;font-family:'Cinzel',serif!important;}}
.preview-box{{background:{BG2};border:0.5px solid {BR};border-radius:10px;padding:16px;min-height:500px;position:relative;overflow:hidden;}}
.prev-inner{{position:relative;z-index:1;}}
.r-name{{font-family:'Cinzel',serif;font-size:16px;color:{T1};text-align:center;}}
.r-role{{font-size:12px;color:{T2};text-align:center;margin-top:2px;}}
.r-contact{{font-size:10px;color:{T3};text-align:center;margin-top:3px;padding-bottom:8px;border-bottom:0.5px solid {BR};margin-bottom:8px;}}
.r-sec{{font-family:'Cinzel',serif;font-size:10px;color:{SC};letter-spacing:2px;border-bottom:0.5px solid {BR};padding-bottom:3px;margin-bottom:5px;margin-top:10px;}}
.r-body{{font-size:11px;color:{T2};line-height:1.7;}}
.empty-box{{display:flex;flex-direction:column;align-items:center;justify-content:center;height:440px;gap:8px;position:relative;z-index:1;text-align:center;}}
.empty-icon{{font-size:40px;}}
.empty-title{{font-family:'Cinzel',serif;font-size:14px;color:{T1};}}
.empty-sub{{font-size:11px;color:{T2};line-height:1.7;}}
.footer{{background:{BG1};padding:10px;text-align:center;font-size:11px;color:{T2};border-top:0.5px solid {BR};margin-top:1rem;}}
.footer span{{color:{SC};}}
hr{{border-color:{BR}!important;}}
</style>
""", unsafe_allow_html=True)

# ─── Topbar ────────────────────────────────────────────────────
col_nav, col_btn = st.columns([5,1])
with col_nav:
    st.markdown(f"""
    <div class="topbar">
        <div style="display:flex;align-items:center;gap:10px;">
            <div class="logo-icon">🦚</div>
            <div>
                <div class="logo-name">MaSu.in</div>
                <div class="logo-sub">AI RESUME BUILDER</div>
            </div>
        </div>
        <div style="font-size:12px;color:{T2};">Jai Jagannath 🙏</div>
    </div>
    """, unsafe_allow_html=True)
with col_btn:
    mode_label = "☀️ Light" if st.session_state.dark_mode else "🌙 Dark"
    if st.button(mode_label):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# ─── Hero ──────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero">
    <h2>Build Your Dream Resume in 30 Seconds</h2>
    <p>AI powered &nbsp;·&nbsp; free &nbsp;·&nbsp; professional &nbsp;·&nbsp; beautiful</p>
    <div class="steps-row">
        <span class="step-pill">1 Choose sections</span>
        <span class="step-pill">2 Fill details</span>
        <span class="step-pill">3 AI generates</span>
        <span class="step-pill">4 Download PDF</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Main Layout ───────────────────────────────────────────────
col1, col2 = st.columns([1,1], gap="medium")

with col1:
    st.markdown('<div class="sec-title">✨ Choose Your Resume Sections</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        show_contact = st.checkbox("📞 Contact",     value=True)
        show_skills  = st.checkbox("⚡ Skills",      value=True)
        show_exp     = st.checkbox("💼 Experience",  value=False)
        show_lang    = st.checkbox("🌐 Languages",   value=False)
        show_ach     = st.checkbox("🌟 Achievements",value=False)
        show_soc     = st.checkbox("🔗 Social Links",value=False)
    with c2:
        show_summary = st.checkbox("📝 Summary",      value=True)
        show_edu     = st.checkbox("🎓 Education",    value=True)
        show_proj    = st.checkbox("🚀 Projects",     value=False)
        show_cert    = st.checkbox("🏆 Certifications",value=False)
        show_hob     = st.checkbox("🎨 Hobbies",     value=False)
        show_ref     = st.checkbox("👥 References",  value=False)

    st.markdown("---")

    # Initialize all variables
    email=phone=city=job_role=skills=""
    education=experience=projects=languages=""
    certifications=achievements=hobbies=""
    linkedin=github=references=""

    st.markdown('<div class="sec-title">👤 Basic Info</div>', unsafe_allow_html=True)
    name = st.text_input("Full Name ⭐", placeholder="Subhankar Padhi")

    if show_contact:
        st.markdown('<div class="sec-title">📞 Contact Info</div>', unsafe_allow_html=True)
        c1,c2 = st.columns(2)
        with c1: email = st.text_input("Email", placeholder="subhankar@gmail.com")
        with c2: phone = st.text_input("Phone", placeholder="9876543210")
        city = st.text_input("City", placeholder="Hyderabad")

    if show_summary:
        st.markdown('<div class="sec-title">📝 Job Role</div>', unsafe_allow_html=True)
        job_role = st.text_input("Target Job Role", placeholder="Python Developer")

    if show_skills:
        st.markdown('<div class="sec-title">⚡ Skills ⭐</div>', unsafe_allow_html=True)
        skills = st.text_area("Skills", placeholder="Python, Streamlit, Machine Learning, SQL", height=80)

    st.markdown('<div class="sec-title">🎓 Education ⭐</div>', unsafe_allow_html=True)
    education = st.text_area("Education", placeholder="B.Tech CSE from XYZ College, 2025", height=80)

    if show_exp:
        st.markdown('<div class="sec-title">💼 Work Experience</div>', unsafe_allow_html=True)
        experience = st.text_area("Experience", placeholder="Python Intern at ABC Company for 3 months", height=80)

    if show_proj:
        st.markdown('<div class="sec-title">🚀 Projects</div>', unsafe_allow_html=True)
        projects = st.text_area("Projects", placeholder="MaSu.in — AI Resume Builder using Python and Groq", height=80)

    if show_lang:
        st.markdown('<div class="sec-title">🌐 Languages</div>', unsafe_allow_html=True)
        languages = st.text_area("Languages", placeholder="Hindi — Native\nEnglish — Fluent\nOdia — Native", height=80)

    if show_cert:
        st.markdown('<div class="sec-title">🏆 Certifications</div>', unsafe_allow_html=True)
        certifications = st.text_area("Certifications", placeholder="Python for Everybody — Coursera", height=80)

    if show_ach:
        st.markdown('<div class="sec-title">🌟 Achievements</div>', unsafe_allow_html=True)
        achievements = st.text_area("Achievements", placeholder="Winner — College Hackathon 2024", height=80)

    if show_hob:
        st.markdown('<div class="sec-title">🎨 Hobbies</div>', unsafe_allow_html=True)
        hobbies = st.text_area("Hobbies", placeholder="Coding, Reading, Photography, Cricket", height=60)

    if show_soc:
        st.markdown('<div class="sec-title">🔗 Social Links</div>', unsafe_allow_html=True)
        c1,c2 = st.columns(2)
        with c1: linkedin = st.text_input("LinkedIn", placeholder="linkedin.com/in/subhankar")
        with c2: github   = st.text_input("GitHub",   placeholder="github.com/subhankar")

    if show_ref:
        st.markdown('<div class="sec-title">👥 References</div>', unsafe_allow_html=True)
        references = st.text_area("References", placeholder="Available on request", height=60)

    st.markdown("---")
    st.markdown(f'<div style="font-size:10px;color:{T3};margin-bottom:8px;">⭐ = Required fields only</div>', unsafe_allow_html=True)
    generate = st.button("🚀 Generate My Resume!")

# ─── Preview ───────────────────────────────────────────────────
with col2:
    st.markdown('<div class="sec-title">📄 Live Resume Preview</div>', unsafe_allow_html=True)

    if generate:
        if name and education:
            with st.spinner("✨ AI is crafting your resume..."):
                try:
                    prompt = f"""Create a professional resume. Only include sections where data is provided. Never write N/A or Not provided.

Name: {name}
{f"Email: {email}" if email else ""}
{f"Phone: {phone}" if phone else ""}
{f"City: {city}" if city else ""}
{f"Target Job Role: {job_role}" if job_role else ""}
Education: {education}
{f"Skills: {skills}" if skills else ""}
{f"Work Experience: {experience}" if experience else ""}
{f"Projects: {projects}" if projects else ""}
{f"Languages: {languages}" if languages else ""}
{f"Certifications: {certifications}" if certifications else ""}
{f"Achievements: {achievements}" if achievements else ""}
{f"Hobbies: {hobbies}" if hobbies else ""}
{f"LinkedIn: {linkedin}" if linkedin else ""}
{f"GitHub: {github}" if github else ""}
{f"References: {references}" if references else ""}

Format professionally with clear sections.
Make it ATS friendly for Indian job market.
If no job role provided write a general summary based on skills and education."""

                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role":"user","content":prompt}]
                    )
                    st.session_state.resume    = response.choices[0].message.content
                    st.session_state.name      = name
                    st.session_state.job_role  = job_role
                    st.session_state.email     = email
                    st.session_state.phone     = phone
                    st.session_state.city      = city

                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Please fill at least Name and Education!")

    if st.session_state.resume:
        st.success("🎉 Your Resume is Ready!")
        contact_parts = [x for x in [
            st.session_state.get('email',''),
            st.session_state.get('phone',''),
            st.session_state.get('city','')
        ] if x]
        contact_line = " · ".join(contact_parts)
        resume_html  = st.session_state.resume.replace('\n','<br>')

        st.markdown(f"""
<div class="preview-box">
{MORPANKH}
<div class="prev-inner">
<div class="r-name">{st.session_state.get('name','')}</div>
{'<div class="r-role">' + st.session_state.get('job_role','') + '</div>' if st.session_state.get('job_role') else ''}
{'<div class="r-contact">' + contact_line + '</div>' if contact_line else ''}
<div class="r-body">{resume_html}</div>
</div>
</div>
""", unsafe_allow_html=True)

        # PDF Download
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Helvetica", size=11)
            pdf.set_auto_page_break(auto=True, margin=15)
            for line in st.session_state.resume.split('\n'):
                pdf.cell(0, 8, line.encode('latin-1','replace').decode('latin-1'), ln=True)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
                pdf.output(f.name)
                with open(f.name,"rb") as pdf_file:
                    st.download_button(
                        label="📥 Download Resume as PDF",
                        data=pdf_file.read(),
                        file_name=f"{st.session_state.get('name','Resume')}_MaSu_Resume.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
            os.unlink(f.name)
        except:
            st.download_button(
                label="📥 Download Resume",
                data=st.session_state.resume,
                file_name=f"{st.session_state.get('name','Resume')}_Resume.txt",
                mime="text/plain",
                use_container_width=True
            )
    else:
        st.markdown(f"""
<div class="preview-box">
{MORPANKH}
<div class="empty-box">
<div class="empty-icon">🦚</div>
<div class="empty-title">Your Resume Will Appear Here</div>
<div class="empty-sub">Choose your sections on the left<br>fill your details and click generate!</div>
</div>
</div>
""", unsafe_allow_html=True)

# ─── Footer ────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    Made with <span>❤</span> by MaSu.in &nbsp;·&nbsp; Jai Jagannath <span>🙏</span>
</div>
""", unsafe_allow_html=True)
