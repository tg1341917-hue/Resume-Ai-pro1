# ==================================================
# IMPORTS
# ==================================================

import streamlit as st
import pdfplumber
import re
import google.generativeai as genai
import plotly.graph_objects as go

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


# ==================================================
# CONFIG
# ==================================================

st.set_page_config(
    page_title="ResumeAI Pro",
    page_icon="🚀",
    layout="wide"
)



# ==================================================
# GEMINI
# ==================================================

try:
    genai.configure(
        api_key=st.secrets["GEMINI_API_KEY"]
    )

    model=genai.GenerativeModel(
        "gemini-3.5-flash"
    )

except:
    model=None



defaults={

    "resume":"",
    "skills":[],
    "missing":[],
    "matched": [],
    "required": [],
    "ats":0,
    "career":0,
    "dream_job": "",
    "improved":"",
    "created":"",
    "complete_ai":""

}


for key,value in defaults.items():

    if key not in st.session_state:

        st.session_state[key]=value



# ==================================================
# UI DESIGN
# ==================================================

st.markdown(
"""

<style>


.stApp{

background:linear-gradient(
135deg,
#020617,
#111827
);

color:white;

}


h1,h2,h3,p,label,div,span{

color:white!important;

}



.title{

text-align:center;

font-size:70px;

font-weight:900;

}


.subtitle{

text-align:center;

font-size:25px;

color:#94a3b8!important;

}



.stButton button{

background:linear-gradient(
90deg,
#2563eb,
#9333ea
);

color:white!important;

border-radius:40px;

padding:15px 40px;

border:none;

font-size:18px;

font-weight:bold;

}


.stTextInput input,
.stTextArea textarea{

background:#111827!important;

color:white!important;

border:2px solid #2563eb!important;

}


[data-testid="stFileUploader"]{

background:#111827;

border-radius:20px;

padding:25px;

border:1px solid #2563eb;

}


[data-testid="stFileUploader"] section{

background:#1e293b!important;

border-radius:15px;

}


[data-testid="stFileUploader"] *{

color:white!important;

}


[data-testid="stFileUploader"] button{

background:#2563eb!important;

color:white!important;

}



.skill{

display:inline-block;

background:#2563eb;

padding:10px 20px;

margin:5px;

border-radius:25px;

}



[data-testid="stMetric"]{

background:#111827;

border:1px solid #2563eb;

padding:20px;

border-radius:20px;

}

/* INPUT PLACEHOLDER FIX */

input::placeholder {

    color: #AAB2C8 !important;

    opacity: 1 !important;

}


textarea::placeholder {

    color: #AAB2C8 !important;

    opacity: 1 !important;

}


/* Actual typed text */

input {

    color: white !important;

}


textarea {

    color: white !important;

}

</style>


""",
unsafe_allow_html=True
)




# ==================================================
# RESUME EXTRACTION
# ==================================================


def extract_text(file):

    text=""

    try:

        with pdfplumber.open(file) as pdf:

            for page in pdf.pages:

                page_text=page.extract_text()

                if page_text:

                    text+=page_text+"\n"

    except:

        pass


    return text




def get_name(text):

    for line in text.split("\n"):

        if len(line.strip())>3:

            return line.strip()

    return "Not Found"




def get_email(text):

    result=re.findall(

        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]+",

        text

    )

    return result[0] if result else "Not Found"




def get_phone(text):

    patterns = [

        r"\+91[\s-]?[6-9]\d{9}",

        r"[6-9]\d{9}"

    ]


    for pattern in patterns:


        result = re.findall(
            pattern,
            text
        )


        if result:


            return result[0]


    return "Not Found"


# ==================================================
# SKILL ENGINE V13
# ==================================================

def detect_skills(text):


    database = [

    # Programming Languages
    "python",
    "java",
    "c++",
    "javascript",
    "sql",

    # AI / ML
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "data science",
    "nlp",
    "natural language processing",
    "computer vision",
    "generative ai",
    "large language models",
    "llm",
    "software engineering",
    "data engineering",
    "api development",

    # Frameworks
    "tensorflow",
    "pytorch",
    "scikit-learn",
    "pandas",
    "numpy",

    # Development
    "html",
    "css",
    "react",
    "node",
    "node.js",
    "flask",
    "streamlit",

    # Database
    "mysql",
    "mongodb",

    # Tools
    "git",
    "github",
    "docker",
    "mlops",

    # Cloud
    "aws",
    "azure",
    "cloud computing",

    # Other Skills
    "mathematics",
    "statistics",
    "mathematics and statistics",
    "problem solving",
    "communication",
    "teamwork",
    "leadership",
    "time management"
    ]


    found=[]


    text=text.lower()


    for skill in database:

        if skill in text:

            found.append(skill)


    return found




# ==================================================
# ATS ENGINE
# ==================================================

# ==================================================
# GOAL BASED ATS ENGINE V16.5
# ==================================================

def calculate_ats(resume, required):

    resume = resume.lower()

    score = 0

    # Resume structure
    sections = [

        "education",
        "skills",
        "project",
        "experience",
        "certification"

    ]

    for section in sections:

        if section in resume:

            score += 8

    matched = 0

    for skill in required:

        if skill.lower() in resume:

            matched += 1

    if len(required) > 0:

        skill_score = (matched / len(required)) * 60

    else:

        skill_score = 0

    final_score = score + skill_score

    if final_score > 100:

        final_score = 100

    return round(final_score)


def ats_breakdown(resume, matched, required):

    resume = resume.lower()

    # ==========================
    # Career Skills Match
    # ==========================

    if len(required) == 0:

        skill_score = 0

    else:

        skill_score = round(
            (len(matched) / len(required)) * 100
        )

    # ==========================
    # Education Relevance
    # ==========================

    education_keywords = [

        "b.tech",
        "btech",
        "computer science",
        "engineering",
        "degree",
        "university",
        "college",
        "education"

    ]

    education_score = 0

    for word in education_keywords:

        if word in resume:

            education_score += 15

    education_score = min(education_score, 100)

    # ==========================
    # Experience Relevance
    # ==========================

    experience_keywords = [

        "experience",
        "intern",
        "project",
        "developed",
        "built",
        "implemented",
        "github"

    ]

    experience_score = 0

    for word in experience_keywords:

        if word in resume:

            experience_score += 15

    experience_score = min(experience_score, 100)

    # ==========================
    # Resume Quality
    # ==========================

    quality = 0

    sections = [

        "education",
        "skills",
        "project",
        "experience",
        "certificate"

    ]

    for section in sections:

        if section in resume:

            quality += 20

    quality = min(quality, 100)

    return {

        "Career Skills Match": skill_score,

        "Education Relevance": education_score,

        "Experience Relevance": experience_score,

        "Resume Quality": quality

    }

# ==================================================
# CAREER ENGINE
# ==================================================

def ask_ai(prompt):

    try:

        if not model:
            return None
        
        print("Calling Gemini...")

        response = model.generate_content(prompt)

        print("Gemini replied")

        if response and hasattr(response, "text"):
            return response.text

        return None

    except Exception as e:

        print(f"GEMINI ERROR: {e}")

        return None
    
CAREER_DATABASE = {

    "ai engineer":[
        "python",
        "machine learning",
        "deep learning",
        "pytorch",
        "mlops",
        "large language models",
        "cloud computing",
        "software engineering",
        "natural language processing",
        "mathematics and statistics"
    ],

    "data scientist":[
        "python",
        "sql",
        "statistics",
        "machine learning",
        "pandas",
        "numpy",
        "data visualization",
        "power bi",
        "tableau",
        "deep learning"
    ],

    "web developer":[
        "html",
        "css",
        "javascript",
        "react",
        "node",
        "mongodb",
        "git",
        "github",
        "api",
        "sql"
    ],

    "chef":[
        "culinary expertise",
        "food safety",
        "menu planning",
        "kitchen management",
        "team leadership",
        "cost control",
        "time management",
        "creativity",
        "communication",
        "problem solving"
    ]
}

# ==================================================
# SMART CAREER SKILL ENGINE V16.6
# ==================================================

def career_analysis(skills, goal):

    goal = goal.strip()

    ai_result = ask_ai(
        f"""
You are an expert career advisor.

For the career:

{goal}

Return ONLY the 10 most important professional skills.

Rules:
- Return comma separated skills only
- No numbering
- No bullets
- No explanation

Example:
Python, SQL, Machine Learning
"""
    )

    required = []

    if ai_result:

        cleaned = (
            ai_result.replace("\n", ",")
                    .replace("•", ",")
                    .replace("-", ",")
        )

        for item in cleaned.split(","):
            item = item.strip().lower()

            if item and item not in required:
                required.append(item)

    if not required:

        required = CAREER_DATABASE.get(goal.lower())

        if required is None:
            required = [
                "career specific knowledge",
                "communication",
                "professional skills",
                "industry experience",
                "portfolio"
            ]

    user_skills = [
        skill.lower().strip()
        for skill in skills
    ]

    matched = []

    missing = []

    for skill in required:

        if any(skill in user_skill or user_skill in skill for user_skill in user_skills):

            matched.append(skill)

        else:

            missing.append(skill)

    if len(required) == 0:

        career = 0

    else:

        career = round(
            len(matched) / len(required) * 100
        )

    return matched, missing, career, required

def hiring(score):

    if score >= 75:
        return "🟢 HIGH"

    elif score >= 40:
        return "🟡 MEDIUM"

    else:
        return "🔴 LOW"
    




def grade(score):

    if score >= 85:
        return "A"

    elif score >= 70:
        return "B"

    elif score >= 50:
        return "C"

    else:
        return "D"


# ==================================================
# SAFE GEMINI AI ENGINE
# ==================================================

# ==================================================
# SMART AI ENGINE V13.1
# ==================================================

# ==================================================
# HYBRID AI ENGINE V13.2
# ==================================================


# ==================================================
# COMPLETE CAREER REPORT
# ==================================================

# ==================================================
# SMART CAREER REPORT ENGINE
# ==================================================
# ==================================================
# SMART COMPLETE AI ENGINE V14
# ==================================================

def generate_everything(resume,skills,missing,ats,career,dream_job):


    ai = ask_ai(
f"""

You are ResumeAI Pro, a professional HR Manager and universal career advisor.

Your task:
Analyze the candidate ONLY according to the selected career goal.


🎯 TARGET CAREER:
{dream_job}


========================
STRICT MATCHING RULES
========================


First compare:

- Candidate education
- Skills
- Projects
- Experience

with the target career.


If the resume background does NOT match {dream_job}:

- Clearly mention LOW compatibility.
- Do NOT force unrelated skills as strengths.
- Do NOT convert programming, AI, or technical skills into another career unless they are actually useful.
- Give missing skills required for {dream_job}.
- Give a beginner friendly roadmap.


If the resume MATCHES {dream_job}:

- Highlight relevant strengths.
- Suggest advanced improvements.


========================
CANDIDATE DETAILS
========================


Resume:

{resume[:4000]}


Detected Skills:

{skills}


Missing Skills:

{missing}


ATS Score:

{ats}%


Career Readiness:

{career}%



Create a complete professional career report:


📊 CAREER MATCH ANALYSIS

Explain how suitable the candidate currently is for {dream_job}.


💪 STRENGTHS

Only mention strengths useful for {dream_job}.


⚠ WEAKNESSES

Mention career specific problems.


🎯 SKILLS TO LEARN

Skills required specifically for {dream_job}.


📚 COMPLETE ROADMAP

Beginner → Intermediate → Advanced roadmap.


🚀 EXPERIENCE / PROJECTS NEEDED

Suggest practical experience required.


📜 CERTIFICATIONS

Suggest useful certifications.


🎤 INTERVIEW PREPARATION

Important interview preparation points.


💰 CAREER GROWTH

Future opportunities in this career.


🏁 FINAL CAREER ADVICE

Give honest HR level advice.


"""
)


    if ai:

        return ai


    return f"""
    # 🎯 Career Report

    ## Target Career
    {dream_job}

    ## ATS Score
    {ats}%

    ## Career Readiness
    {career}%

    ## Skills Found
    {", ".join(skills)}

    ## Skills To Learn
    {", ".join(missing)}

    # Recommendation

    Your resume has been analyzed successfully.

    ### To improve your chances of getting shortlisted:

    - 📚 Learn the missing skills listed above.
    - 💻 Build 2–3 projects related to your target career.
    - 🏆 Add relevant certifications to strengthen your resume.
    - 📈 Include measurable achievements and practical experience.
    - 🔄 Update your resume and run the analysis again to track your progress.

    ### Overall Advice

    Consistently improving your technical skills and maintaining a strong, ATS-friendly resume will significantly increase your career readiness and hiring potential.
    """


# ==================================================
# HYBRID RESUME IMPROVER
# ==================================================

def improve_resume(resume):


    ai=ask_ai(
        f"""

Improve this resume professionally.

Make it ATS friendly.

{resume}

"""
    )


    if ai:

        return ai



    # BACKUP SYSTEM

    return f"""

# PROFESSIONAL RESUME


{resume}



==============================


AI OPTIMIZATION SUGGESTIONS


✔ Add measurable achievements

✔ Use action verbs:
Developed
Created
Implemented
Optimized


✔ Improve project descriptions


Example:


Before:

Made AI project


After:

Developed an AI powered application using Python and Machine Learning improving automation efficiency.


✔ Add:

- GitHub profile
- LinkedIn profile
- Certifications
- Real world projects


✔ Keep resume ATS friendly

"""



# ==================================================
# AI RESUME BUILDER
# ==================================================

# ==================================================
# HYBRID RESUME BUILDER
# ==================================================

def build_resume(details):


    ai=ask_ai(

        f"""

Create professional ATS resume:

{details}

"""

    )


    if ai:


        return ai



    return f"""

# PROFESSIONAL RESUME


{details}



PROFESSIONAL SUMMARY


Motivated technology enthusiast with strong problem solving skills and passion for building software solutions.



TECHNICAL SKILLS


Add your programming languages, frameworks, databases and tools.



PROJECTS


Mention:

Project Name

Technology Used

Problem Solved

Features



ACHIEVEMENTS


Add certifications, awards and accomplishments.



CAREER OBJECTIVE


To contribute technical knowledge and continuously improve as a professional developer.

"""



# ==================================================
# PREMIUM RESUME PDF ENGINE V15.5
# ==================================================

# ==================================================
# DESIGNER RESUME PDF ENGINE V15.6
# ==================================================

def create_pdf(text):

    filename="ResumeAI_Designer_Resume.pdf"


    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle
    )

    from reportlab.lib.styles import (
        getSampleStyleSheet,
        ParagraphStyle
    )

    from reportlab.lib.pagesizes import letter

    from reportlab.lib.enums import TA_CENTER

    from reportlab.lib import colors



    doc=SimpleDocTemplate(

        filename,

        pagesize=letter,

        rightMargin=45,

        leftMargin=45,

        topMargin=40,

        bottomMargin=40

    )



    styles=getSampleStyleSheet()



    story=[]



    # ------------------------------
    # CUSTOM STYLES
    # ------------------------------


    name_style=ParagraphStyle(

        "NameStyle",

        fontSize=24,

        alignment=TA_CENTER,

        textColor=colors.white,

        spaceAfter=10

    )



    header_text=ParagraphStyle(

        "HeaderText",

        fontSize=10,

        alignment=TA_CENTER,

        textColor=colors.white

    )



    heading_style=ParagraphStyle(

        "Heading",

        fontSize=13,

        textColor=colors.HexColor("#1E3A8A"),

        spaceBefore=14,

        spaceAfter=8

    )



    body_style=ParagraphStyle(

        "Body",

        parent=styles["BodyText"],

        fontSize=10,

        leading=15

    )





    lines=[

        x.strip()

        for x in text.split("\n")

        if x.strip()

    ]



    if len(lines)==0:

        return filename



    # ------------------------------
    # TOP BLUE HEADER
    # ------------------------------


    name=lines[0].replace("*","")



    header=[

        [

            Paragraph(

                name.upper(),

                name_style

            )

        ]

    ]



    header_table=Table(

        header,

        colWidths=[500]

    )



    header_table.setStyle(

        TableStyle(

            [

            ("BACKGROUND",(0,0),(-1,-1),
             colors.HexColor("#1E3A8A")),

            ("TOPPADDING",(0,0),(-1,-1),20),

            ("BOTTOMPADDING",(0,0),(-1,-1),20),

            ]

        )

    )



    story.append(header_table)


    story.append(

        Spacer(1,20)

    )



    headings=[

        "SUMMARY",

        "PROFESSIONAL SUMMARY",

        "CONTACT",

        "SKILLS",

        "TECHNICAL SKILLS",

        "EDUCATION",

        "PROJECTS",

        "EXPERIENCE",

        "CERTIFICATIONS",

        "ACHIEVEMENTS"

    ]



    # ------------------------------
    # BODY
    # ------------------------------


    for line in lines[1:]:



        clean=line.replace("*","")



        if clean.upper() in headings:


            story.append(

                Paragraph(

                    clean.upper(),

                    heading_style

                )

            )



        else:



            if clean.startswith("-"):

                clean="• "+clean[1:]



            story.append(

                Paragraph(

                    clean,

                    body_style

                )

            )



        story.append(

            Spacer(1,6)

        )




    doc.build(story)



    return filename

# ==================================================
# MAIN WEBSITE
# ==================================================

st.markdown(
"""

<div class="title">
🚀 ResumeAI Pro
</div>

<div class="subtitle">
AI Resume Analyzer • Resume Builder • Career Assistant
</div>

<br>

""",
unsafe_allow_html=True
)


mode = st.radio(
    "Choose Service",
    [
        "🔍 Analyze Resume",
        "📄 Create Resume"
    ]
)





# ==================================================
# RESUME ANALYZER
# ==================================================

if mode=="🔍 Analyze Resume":


    uploaded = st.file_uploader(
        "📄 Upload Resume PDF",
        type=["pdf"]
    )


    dream_job = st.text_input(
    "🎯 Enter Your Dream Job / Career Goal",
    placeholder="Example: AI Engineer, Data Scientist, Web Developer"
)



    if st.button("🚀 Analyze Resume"):


        if uploaded and dream_job:


            text = extract_text(uploaded)


            skills = detect_skills(text)


            matched, missing, career, required = career_analysis(
                skills,
                dream_job
            )

            st.session_state.required = required


            


            ats = calculate_ats(
                text,

                required
                
            )


            st.session_state.resume=text
            st.session_state.skills=skills
            st.session_state.missing=missing
            st.session_state.career=career
            st.session_state.matched =matched
            st.session_state.required =required
            st.session_state.ats=ats
            st.session_state.dream_job=dream_job


            st.session_state.complete_ai=""
            st.session_state.improved=""

            with st.spinner(
                "📄 Analyzing Resume..."
            ):

                st.session_state.complete_ai = generate_everything(

                    text,

                    skills,

                    missing,

                    ats,

                    career,

                    dream_job

                )


            st.success(
                "Resume analyzed successfully 🚀"
            )


        else:


            st.warning(
                "Please upload resume and enter job description"
            )






# ==================================================
# ANALYSIS DASHBOARD
# ==================================================

if mode=="🔍 Analyze Resume" and st.session_state.resume:


    text=st.session_state.resume

    tab1,tab2,tab3,tab4 = st.tabs(

        [

        "📊 Overview",

        "🤖 AI Report",

        "✨ Resume",

        "🎯 Skills"

        ]

    )

    with tab1:

        st.header("👤 Candidate Details")


        a,b,c = st.columns(3)


        a.metric(
            "Name",
            get_name(text)
        )


        b.metric(
            "Email",
            get_email(text)
        )


        c.metric(
            "Phone",
            get_phone(text)
        )






        st.header("📊 Career Dashboard")


        c1,c2,c3,c4=st.columns(4)



        c1.metric(
            "ATS Score",
            str(st.session_state.ats)+"%"
        )


        c2.metric(
            "Career Ready",
            str(st.session_state.career)+"%"
        )


        c3.metric(
            "Hiring Chance",
            hiring(st.session_state.career)
        )

        c4.metric(
            "Resume Grade",
            grade(st.session_state.ats)
        )

        st.subheader(
            "📊 ATS Score Breakdown"
        )


        breakdown = ats_breakdown(
        text,
        st.session_state.matched,
        st.session_state.required
        
    )



        for name,value in breakdown.items():


            st.write(
                name
            )


            st.progress(
                value/100
            )


            st.caption(
                str(value)+"%"
            )


        





        chart = go.Figure(

            go.Indicator(

                mode="gauge+number",

                value=st.session_state.ats

            )

        )


        st.plotly_chart(chart)






        st.header("🛠 Skills Found")


        if st.session_state.skills:


            skill_html=""


            for skill in st.session_state.skills:


                skill_html+=(
                    f"<span class='skill'>{skill.upper()}</span>"
                )


            st.markdown(
                skill_html,
                unsafe_allow_html=True
            )


        else:


            st.warning(
                "No major technical skills detected"
            )







    with tab4:

        st.header("🎯 Skills To Improve")

        career_match = breakdown["Career Skills Match"]

        if career_match >= 80:
            st.success("Excellent skill match 🚀")

        elif career_match >= 60:
            st.info("Good career match 👍")

        elif career_match >= 40:
            st.warning("Average career match ⚠️")

        else:
            st.error("Poor career match. Learn these skills:")

        if st.session_state.missing:

            st.markdown("### 📚 Skills To Learn")

            for skill in st.session_state.missing:
                st.markdown(f"- **{skill.title()}**")




    # AI REPORT

    with tab2:

        st.header("🤖 AI Career Report")

        if st.session_state.complete_ai:
            st.write(st.session_state.complete_ai)









    # RESUME IMPROVER

    with tab3:

        if st.button(
            "✨ Improve Resume With AI"
        ):


            if st.session_state.improved=="":


                with st.spinner(
                    "Creating professional resume..."
                ):


                    st.session_state.improved=improve_resume(
                        text
                    )





        if st.session_state.improved:


            st.header(
                "✨ Improved Resume"
            )


            st.write(
                st.session_state.improved
            )



            pdf=create_pdf(
                st.session_state.improved
            )



            with open(pdf,"rb") as file:


                st.download_button(

                    "⬇ Download Improved Resume PDF",

                    file,

                    "Improved_Resume.pdf"

                )









# ==================================================
# AI RESUME BUILDER
# ==================================================

if mode=="📄 Create Resume":


    st.header(
        "📄 AI Professional Resume Builder"
    )


    col1,col2=st.columns(2)


    with col1:


        name=st.text_input("Name")


        email=st.text_input("Email")


        phone=st.text_input("Phone")


    with col2:


        linkedin=st.text_input("LinkedIn")


        github=st.text_input("GitHub")


        role=st.text_input("Target Role")




    education=st.text_area(
        "🎓 Education"
    )


    skills=st.text_area(
        "💻 Skills"
    )


    projects=st.text_area(
        "🚀 Projects"
    )


    experience=st.text_area(
        "💼 Experience"
    )


    certificates=st.text_area(
        "🏆 Certifications"
    )





    if st.button(
        "🚀 Generate Resume"
    ):


        details=f"""

Name:
{name}

Email:
{email}

Phone:
{phone}

LinkedIn:
{linkedin}

GitHub:
{github}

Role:
{role}

Education:
{education}

Skills:
{skills}

Projects:
{projects}

Experience:
{experience}

Certificates:
{certificates}

"""


        with st.spinner(
            "Building resume..."
        ):


            st.session_state.created=build_resume(
                details
            )







    if st.session_state.created:


        st.header(
            "✨ Generated Resume"
        )


        st.write(
            st.session_state.created
        )


        pdf=create_pdf(
            st.session_state.created
        )


        with open(pdf,"rb") as file:


            st.download_button(

                "⬇ Download Resume PDF",

                file,

                "ResumeAI.pdf"

            )









# ==================================================
# FOOTER
# ==================================================

st.markdown(
"""

<br><br>

<center>

<h3>
🚀 ResumeAI Pro
</h3>

<p>
Python • Streamlit • Machine Learning • Gemini AI
</p>

</center>

""",
unsafe_allow_html=True
)
