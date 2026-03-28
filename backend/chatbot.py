import nltk
import re
import spacy
import time
import random
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from textblob import TextBlob
from difflib import SequenceMatcher
import os

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')
    nltk.download('averaged_perceptron_tagger')

class CollegeChatbot:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        # Load spaCy model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            print("Warning: spaCy model not found. Some features may be limited.")
            self.nlp = None
        
        # Comprehensive knowledge base with proper formatting
        self.knowledge_base = {
            'greeting': {
                'patterns': [
                    'hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening', 
                    'namaste', 'hola', 'howdy', 'whats up', 'sup'
                ],
                'responses': [
                    "Hello! Welcome to College Enquiry Chatbot. How can I help you today?",
                    "Hi there! I'm here to answer all your college-related questions.",
                    "Greetings! How can I assist you with your college enquiry?"
                ],
                'keywords': ['hi', 'hello', 'hey', 'greeting', 'namaste', 'howdy']
            },
            'admission_process': {
                'patterns': [
                    'admission process', 'how to apply', 'apply for admission', 'admission procedure',
                    'how can i get admission', 'admission steps', 'process of admission',
                    'what is the admission process', 'tell me about admission'
                ],
                'responses': [
                    "📋 **Admission Process**\n\n"
                    "1️⃣ Fill the online application form on our website\n\n"
                    "2️⃣ Upload required documents\n"
                    "   • 10th and 12th marksheets\n"
                    "   • Transfer certificate\n"
                    "   • ID proof (Aadhar/Passport)\n"
                    "   • Recent photographs\n\n"
                    "3️⃣ Pay the application fee of ₹500\n\n"
                    "4️⃣ Appear for entrance test and personal interview\n\n"
                    "5️⃣ Check results online on the declared date\n\n"
                    "6️⃣ Complete fee payment to confirm your seat"
                ],
                'keywords': ['admission', 'apply', 'procedure', 'process', 'steps']
            },
            'admission_dates': {
                'patterns': [
                    'admission dates', 'when does admission start', 'admission deadline', 
                    'last date to apply', 'admission schedule', 'when can i apply',
                    'application deadline', 'start date', 'important dates'
                ],
                'responses': [
                    "📅 **Important Admission Dates 2026**\n\n"
                    "• Application Start: **June 1, 2026**\n\n"
                    "• Last Date to Apply: **July 15, 2026**\n\n"
                    "• Entrance Test: **July 20, 2026**\n\n"
                    "• Result Declaration: **July 30, 2026**\n\n"
                    "• Counseling Starts: **August 5, 2026**\n\n"
                    "• Classes Begin: **August 20, 2026**"
                ],
                'keywords': ['date', 'start', 'deadline', 'when', 'schedule', 'timeline']
            },
            'admission_eligibility': {
                'patterns': [
                    'eligibility', 'who can apply', 'qualification required', 'minimum marks',
                    'eligibility criteria', 'requirements for admission', 'what are the requirements',
                    'am i eligible', 'qualifications needed'
                ],
                'responses': [
                    "🎯 **Eligibility Criteria**\n\n"
                    "**For Undergraduate (UG) Courses:**\n"
                    "• Minimum 50% marks in 10+2 (45% for reserved categories)\n"
                    "• Students appearing for final exams can also apply\n\n"
                    "**For Postgraduate (PG) Courses:**\n"
                    "• Bachelor's degree with minimum 50% marks\n"
                    "• Relevant undergraduate degree required for specialized programs\n\n"
                    "**Note:** There is no upper age limit for any course."
                ],
                'keywords': ['eligibility', 'qualification', 'marks', 'eligible', 'requirements']
            },
            'library_timing': {
                'patterns': [
                    'library timing', 'library hours', 'when library opens', 'library closes',
                    'library schedule', 'what time library open', 'library open time',
                    'library close time', 'library working hours', 'timings of library'
                ],
                'responses': [
                    "🕒 **Library Timings**\n\n"
                    "• Monday to Friday: **8:00 AM to 8:00 PM**\n\n"
                    "• Saturday: **9:00 AM to 5:00 PM**\n\n"
                    "• Sunday: **Closed**\n\n"
                    "• Public Holidays: **Closed**\n\n"
                    "📌 **Note:** The digital library is accessible 24/7 through the student portal."
                ],
                'keywords': ['timing', 'hour', 'open', 'close', 'schedule', 'when']
            },
            'library_books': {
                'patterns': [
                    'library books', 'book collection', 'how many books', 'books available',
                    'books in library', 'what books are there', 'book count',
                    'number of books', 'book list', 'collection of books',
                    'what books do you have'
                ],
                'responses': [
                    "📚 **Library Collection**\n\n"
                    "• **Total Books:** 75,000+ across all subjects\n\n"
                    "• **National Journals:** 100+ subscriptions\n\n"
                    "• **International Journals:** 50+ subscriptions\n\n"
                    "• **E-Books:** 25,000+ digital titles\n\n"
                    "• **Research Papers:** 50,000+ access\n\n"
                    "• **Thesis & Dissertations:** 1,000+ student works\n\n"
                    "• **Previous Year Papers:** Complete digital archive"
                ],
                'keywords': ['books', 'collection', 'journals', 'papers', 'thesis', 'archives']
            },
            'library_digital': {
                'patterns': [
                    'digital library', 'e-library', 'online resources', 'e-books', 'online journals',
                    'digital resources', 'online books', 'internet library', 'virtual library',
                    'online access', 'remote access', 'digital collection'
                ],
                'responses': [
                    "💻 **Digital Library Resources**\n\n"
                    "• **E-Books:** 25,000+ titles\n"
                    "  - Springer, Elsevier, Wiley\n\n"
                    "• **Online Courses:** Free access\n"
                    "  - Coursera, Udemy, edX\n\n"
                    "• **Research Databases:**\n"
                    "  - IEEE, ACM, J-Gate, Scopus\n\n"
                    "• **Previous Papers:** Digital archive of last 10 years\n\n"
                    "• **Remote Access:** Available 24/7 from anywhere\n\n"
                    "• **Mobile App:** Access library on your smartphone"
                ],
                'keywords': ['digital', 'online', 'ebook', 'elibrary', 'virtual', 'remote']
            },
            'courses_bca': {
                'patterns': [
                    'bca', 'bachelor of computer applications', 'computer applications course',
                    'tell me about bca', 'bca details', 'bca information', 'bca program',
                    'what is bca', 'bca course', 'about bca'
                ],
                'responses': [
                    "💻 **BCA (Bachelor of Computer Applications)**\n\n"
                    "**📊 Program Overview**\n"
                    "• Duration: **3 years** (6 semesters)\n"
                    "• Intake Capacity: **120 students**\n"
                    "• Annual Fees: **₹45,000**\n\n"
                    "**📚 Core Subjects**\n"
                    "• Programming Languages: C, C++, Java, Python\n"
                    "• Database Management Systems\n"
                    "• Web Development\n"
                    "• Computer Networks\n"
                    "• Operating Systems\n"
                    "• Software Engineering\n\n"
                    "**💼 Career Options**\n"
                    "• Software Developer\n"
                    "• Web Designer\n"
                    "• System Analyst\n"
                    "• Database Administrator\n"
                    "• IT Consultant"
                ],
                'keywords': ['bca', 'computer applications']
            },
            'courses_mca': {
                'patterns': [
                    'mca', 'master of computer applications', 'mca details', 'mca information',
                    'tell me about mca', 'what is mca', 'mca program', 'mca course'
                ],
                'responses': [
                    "🎓 **MCA (Master of Computer Applications)**\n\n"
                    "**📊 Program Overview**\n"
                    "• Duration: **2 years** (4 semesters)\n"
                    "• Intake Capacity: **60 students**\n"
                    "• Annual Fees: **₹60,000**\n"
                    "• Eligibility: BCA or B.Sc CS with Mathematics\n\n"
                    "**📚 Advanced Subjects**\n"
                    "• Advanced Java Programming\n"
                    "• Machine Learning\n"
                    "• Cloud Computing\n"
                    "• Cyber Security\n"
                    "• Big Data Analytics\n"
                    "• Mobile App Development\n\n"
                    "**💼 Career Options**\n"
                    "• Software Architect\n"
                    "• IT Consultant\n"
                    "• Project Manager\n"
                    "• Senior Developer\n"
                    "• Technical Lead"
                ],
                'keywords': ['mca', 'master of computer applications']
            },
            'courses_mba': {
                'patterns': [
                    'mba', 'master of business administration', 'mba details', 'mba information',
                    'tell me about mba', 'what is mba', 'mba program', 'mba course',
                    'business administration'
                ],
                'responses': [
                    "📊 **MBA (Master of Business Administration)**\n\n"
                    "**📊 Program Overview**\n"
                    "• Duration: **2 years** (4 semesters)\n"
                    "• Intake Capacity: **60 students**\n"
                    "• Annual Fees: **₹80,000**\n"
                    "• Eligibility: Any graduate with 50% marks\n\n"
                    "**🎯 Specializations**\n"
                    "• Marketing Management\n"
                    "• Finance Management\n"
                    "• Human Resources\n"
                    "• Operations Management\n"
                    "• Business Analytics\n\n"
                    "**💼 Career Options**\n"
                    "• Business Analyst\n"
                    "• Marketing Manager\n"
                    "• HR Manager\n"
                    "• Financial Analyst\n"
                    "• Operations Manager"
                ],
                'keywords': ['mba', 'business administration']
            },
            'fees_bca': {
                'patterns': [
                    'bca fee', 'bca fees', 'bca cost', 'bca payment', 'how much is bca',
                    'bca course fee', 'bca expenses', 'bca total fee', 'fee for bca'
                ],
                'responses': [
                    "💰 **BCA Fee Structure (per year)**\n\n"
                    "**Breakdown:**\n"
                    "• Tuition Fee: ₹45,000\n"
                    "• Laboratory Fee: ₹5,000\n"
                    "• Library Fee: ₹3,000\n"
                    "• Sports Fee: ₹2,000\n"
                    "• Examination Fee: ₹5,000\n\n"
                    "**Total: ₹60,000 per year**\n\n"
                    "**Hostel Fee (optional):** ₹70,000 per year (includes mess)\n\n"
                    "**Payment Options:**\n"
                    "• One-time annual payment (5% discount)\n"
                    "• Semester-wise (50% each semester)\n"
                    "• Monthly installments (with nominal interest)"
                ],
                'keywords': ['bca fee', 'bca cost', 'bca payment']
            },
            'fees_mca': {
                'patterns': [
                    'mca fee', 'mca fees', 'mca cost', 'mca payment', 'how much is mca',
                    'mca course fee', 'mca expenses', 'fee for mca'
                ],
                'responses': [
                    "💰 **MCA Fee Structure (per year)**\n\n"
                    "**Breakdown:**\n"
                    "• Tuition Fee: ₹60,000\n"
                    "• Laboratory Fee: ₹7,000\n"
                    "• Library Fee: ₹3,000\n"
                    "• Sports Fee: ₹2,000\n"
                    "• Examination Fee: ₹6,000\n\n"
                    "**Total: ₹78,000 per year**\n\n"
                    "**Hostel Fee (optional):** ₹70,000 per year (includes mess)"
                ],
                'keywords': ['mca fee', 'mca cost', 'mca payment']
            },
            'fees_mba': {
                'patterns': [
                    'mba fee', 'mba fees', 'mba cost', 'mba payment', 'how much is mba',
                    'mba course fee', 'mba expenses', 'fee for mba'
                ],
                'responses': [
                    "💰 **MBA Fee Structure (per year)**\n\n"
                    "**Breakdown:**\n"
                    "• Tuition Fee: ₹80,000\n"
                    "• Library Fee: ₹5,000\n"
                    "• Sports Fee: ₹2,000\n"
                    "• Examination Fee: ₹8,000\n\n"
                    "**Total: ₹95,000 per year**\n\n"
                    "**Hostel Fee (optional):** ₹70,000 per year (includes mess)"
                ],
                'keywords': ['mba fee', 'mba cost', 'mba payment']
            },
            'fees_general': {
                'patterns': [
                    'fees', 'fee structure', 'course fees', 'how much does it cost', 'payment',
                    'college fees', 'tuition fee', 'total fee', 'what is the fee',
                    'fee details', 'cost of courses'
                ],
                'responses': [
                    "💰 **Course-wise Fee Range (per year)**\n\n"
                    "• **BCA:** ₹45,000 - ₹60,000\n"
                    "• **B.Sc Computer Science:** ₹40,000 - ₹55,000\n"
                    "• **B.Com:** ₹35,000 - ₹50,000\n"
                    "• **MCA:** ₹60,000 - ₹78,000\n"
                    "• **MBA:** ₹80,000 - ₹95,000\n\n"
                    "💡 **For specific course fees, ask:**\n"
                    "• \"BCA fees\"\n"
                    "• \"MBA fee structure\"\n"
                    "• \"How much does MCA cost\""
                ],
                'keywords': ['fee', 'fees', 'cost', 'payment', 'expense', 'tuition']
            },
            'placement_stats': {
                'patterns': [
                    'placement statistics', 'placement record', 'placement data', 'placement history',
                    'placement report', 'placement details', 'tell me about placements',
                    'how is placement', 'placement scenario', 'placement percentage'
                ],
                'responses': [
                    "📊 **Placement Statistics 2025**\n\n"
                    "**Key Metrics:**\n"
                    "• Total Students Placed: **450+**\n"
                    "• Placement Percentage: **92%**\n"
                    "• Average Package: **₹7.2 LPA**\n"
                    "• Highest Package: **₹25 LPA** (International)\n"
                    "• Students with Multiple Offers: **120+**\n"
                    "• International Offers: **15**\n\n"
                    "**Top Recruiters:**\n"
                    "• TCS, Infosys, Wipro\n"
                    "• Accenture, Amazon, Microsoft\n"
                    "• Deloitte, PwC, KPMG"
                ],
                'keywords': ['placement', 'statistics', 'record', 'data', 'report', 'percentage']
            },
            'placement_companies': {
                'patterns': [
                    'which companies', 'recruiters', 'top companies', 'visiting companies',
                    'companies visiting', 'recruitment companies', 'placement companies',
                    'who visits', 'list of companies', 'company names'
                ],
                'responses': [
                    "🏢 **Top Recruiting Companies**\n\n"
                    "**IT & Software:**\n"
                    "• TCS\n"
                    "• Infosys\n"
                    "• Wipro\n"
                    "• HCL\n"
                    "• Tech Mahindra\n"
                    "• Cognizant\n\n"
                    "**Tech Giants:**\n"
                    "• Microsoft\n"
                    "• Google\n"
                    "• Amazon\n"
                    "• Adobe\n\n"
                    "**Consulting Firms:**\n"
                    "• Accenture\n"
                    "• Deloitte\n"
                    "• PwC\n"
                    "• KPMG\n\n"
                    "**Banking & Finance:**\n"
                    "• HDFC Bank\n"
                    "• ICICI Bank\n"
                    "• Axis Bank"
                ],
                'keywords': ['companies', 'recruiters', 'visiting', 'recruitment']
            },
            'placement_package': {
                'patterns': [
                    'average package', 'average salary', 'highest package', 'salary range',
                    'salary package', 'how much salary', 'package details', 'compensation',
                    'what is the average', 'what is the highest', 'salary offered'
                ],
                'responses': [
                    "💰 **Placement Package Details 2025**\n\n"
                    "**Overall Packages:**\n"
                    "• **Average Package:** ₹7.2 LPA\n"
                    "• **Median Package:** ₹6.5 LPA\n"
                    "• **Highest Package:** ₹25 LPA (International)\n"
                    "• **Minimum Package:** ₹3.5 LPA\n\n"
                    "**Top Performer Packages:**\n"
                    "• Top 10% Students: **₹15+ LPA**\n"
                    "• Top 25% Students: **₹10+ LPA**\n\n"
                    "**Branch-wise Average:**\n"
                    "• CSE/IT: ₹8.5 LPA\n"
                    "• MBA: ₹7.8 LPA\n"
                    "• MCA: ₹6.5 LPA\n"
                    "• BCA: ₹5.2 LPA"
                ],
                'keywords': ['package', 'salary', 'average', 'highest', 'ctc', 'lpa']
            },
            'hostel_general': {
                'patterns': [
                    'hostel', 'accommodation', 'hostel facility', 'dormitory',
                    'hostel details', 'tell me about hostel', 'hostel information',
                    'where to stay', 'living facilities', 'campus accommodation'
                ],
                'responses': [
                    "🏠 **Hostel Facilities Overview**\n\n"
                    "**Facilities:**\n"
                    "• Separate hostels for Boys and Girls\n"
                    "• Total Capacity: **900 students**\n"
                    "  - Boys: 500 students\n"
                    "  - Girls: 400 students\n\n"
                    "**Room Options:**\n"
                    "• Single occupancy\n"
                    "• Double sharing\n"
                    "• Triple sharing\n\n"
                    "**Annual Fee:** ₹70,000 (includes mess)\n\n"
                    "**Amenities:**\n"
                    "• High-speed Wi-Fi\n"
                    "• Modern gymnasium\n"
                    "• Common room with TV\n"
                    "• Laundry service\n"
                    "• 24/7 security with CCTV\n"
                    "• Biometric entry system\n\n"
                    "💡 **For specific details, ask:**\n"
                    "• \"Boys hostel\"\n"
                    "• \"Girls hostel\"\n"
                    "• \"Mess facilities\""
                ],
                'keywords': ['hostel', 'accommodation', 'dorm', 'stay', 'living']
            },
            'hostel_boys': {
                'patterns': [
                    'boys hostel', 'hostel for boys', 'boys accommodation',
                    'where do boys stay', 'boys living', 'hostel for male'
                ],
                'responses': [
                    "👨 **Boys Hostel Details**\n\n"
                    "**Blocks:** 5 (A, B, C, D, E)\n"
                    "**Total Capacity:** 500 students\n\n"
                    "**Room Fees (per year):**\n"
                    "• Single Room: ₹80,000\n"
                    "• Double Sharing: ₹70,000\n"
                    "• Triple Sharing: ₹60,000\n\n"
                    "**Amenities:**\n"
                    "• High-speed Wi-Fi\n"
                    "• Fully equipped gym\n"
                    "• TV and recreation room\n"
                    "• Table tennis and indoor games\n"
                    "• Laundry service\n\n"
                    "**Location:** North Campus, near academic blocks"
                ],
                'keywords': ['boys hostel', 'boys accommodation']
            },
            'hostel_girls': {
                'patterns': [
                    'girls hostel', 'hostel for girls', 'girls accommodation',
                    'where do girls stay', 'girls living', 'ladies hostel',
                    'hostel for female'
                ],
                'responses': [
                    "👩 **Girls Hostel Details**\n\n"
                    "**Blocks:** 4 (G1, G2, G3, G4)\n"
                    "**Total Capacity:** 400 students\n\n"
                    "**Room Fees (per year):**\n"
                    "• Single Room: ₹80,000\n"
                    "• Double Sharing: ₹70,000\n"
                    "• Triple Sharing: ₹60,000\n\n"
                    "**Amenities:**\n"
                    "• High-speed Wi-Fi\n"
                    "• Gym and yoga room\n"
                    "• Common room with TV\n"
                    "• Indoor games\n"
                    "• Laundry service\n\n"
                    "**Safety Features:**\n"
                    "• Female wardens\n"
                    "• 24/7 CCTV surveillance\n"
                    "• Security guards\n"
                    "• Biometric entry\n\n"
                    "**Location:** South Campus, near library"
                ],
                'keywords': ['girls hostel', 'girls accommodation', 'ladies hostel']
            },
            'mess': {
                'patterns': [
                    'mess', 'food', 'canteen', 'dining', 'food facility',
                    'mess food', 'canteen food', 'dining hall', 'what food',
                    'meal', 'breakfast', 'lunch', 'dinner'
                ],
                'responses': [
                    "🍽️ **Mess and Dining Facilities**\n\n"
                    "**Menu Options:**\n"
                    "• North Indian cuisine\n"
                    "• South Indian cuisine\n"
                    "• Chinese cuisine\n"
                    "• Jain food available on request\n\n"
                    "**Meal Timings:**\n"
                    "• **Breakfast:** 7:30 AM to 9:00 AM\n"
                    "• **Lunch:** 12:00 PM to 2:00 PM\n"
                    "• **Dinner:** 7:00 PM to 9:00 PM\n\n"
                    "**Options:**\n"
                    "• Vegetarian and Non-vegetarian available\n"
                    "• Separate counters for both\n\n"
                    "**Monthly Fee:** Included in hostel fees\n"
                    "**Canteen:** Open 8 AM to 10 PM for snacks and beverages"
                ],
                'keywords': ['mess', 'food', 'canteen', 'dining', 'meal']
            },
            'sports': {
                'patterns': [
                    'sports', 'games', 'sports facility', 'cricket', 'football', 'basketball',
                    'sports ground', 'gym', 'fitness', 'sports complex', 'athletics'
                ],
                'responses': [
                    "⚽ **Sports Facilities**\n\n"
                    "**Outdoor Facilities:**\n"
                    "• Cricket ground with practice nets\n"
                    "• Football field (FIFA standard)\n"
                    "• Basketball court (2 courts)\n"
                    "• Volleyball court\n"
                    "• Tennis court\n"
                    "• 400m athletics track\n\n"
                    "**Indoor Facilities:**\n"
                    "• Badminton courts\n"
                    "• Table tennis\n"
                    "• Chess and carrom\n"
                    "• Modern gymnasium\n\n"
                    "**Timings:** 6:00 AM to 8:00 PM\n"
                    "**Professional coaches** available for all sports\n\n"
                    "**Achievements:** State champions in Cricket, Basketball, and Athletics"
                ],
                'keywords': ['sports', 'games', 'cricket', 'football', 'basketball', 'gym']
            },
            'transport': {
                'patterns': [
                    'transport', 'bus', 'shuttle', 'conveyance', 'college bus',
                    'bus facility', 'transportation', 'how to reach', 'commute'
                ],
                'responses': [
                    "🚌 **College Transport Facilities**\n\n"
                    "**Fleet:** 15 college buses covering major routes\n"
                    "**Routes:** 12 routes across the city\n\n"
                    "**Timings:**\n"
                    "• First bus: 7:00 AM\n"
                    "• Last bus: 6:00 PM\n\n"
                    "**Fees:**\n"
                    "• Annual: ₹15,000\n"
                    "• Monthly Pass: ₹1,500\n\n"
                    "**Features:**\n"
                    "• GPS tracking on all buses\n"
                    "• Female attendants on all buses\n"
                    "• Live tracking on student app\n"
                    "• Pickup and drop at designated stops"
                ],
                'keywords': ['transport', 'bus', 'shuttle', 'conveyance', 'commute']
            },
            'scholarship': {
                'patterns': [
                    'scholarship', 'financial aid', 'fee concession', 'financial assistance',
                    'education loan', 'scholarship opportunities', 'aid'
                ],
                'responses': [
                    "🎓 **Scholarship Opportunities**\n\n"
                    "**1. Merit-Based Scholarship**\n"
                    "• 90% and above: **100%** tuition fee waiver\n"
                    "• 85-89%: **50%** tuition fee waiver\n"
                    "• 80-84%: **25%** tuition fee waiver\n\n"
                    "**2. Need-Based Financial Aid**\n"
                    "• Up to ₹50,000 per year based on family income\n"
                    "• Requires income certificate and documents\n\n"
                    "**3. Sports Quota Scholarship**\n"
                    "• 30% fee concession for state/national level players\n\n"
                    "**4. Government Scholarships**\n"
                    "• SC/ST/OBC scholarships as per government norms\n"
                    "• Minority scholarship schemes\n\n"
                    "**Application Deadline:** August 31st annually"
                ],
                'keywords': ['scholarship', 'financial aid', 'concession', 'assistance']
            },
            'contact': {
                'patterns': [
                    'contact', 'phone', 'email', 'address', 'reach', 'call', 'contact number',
                    'phone number', 'email id', 'college address', 'where is college',
                    'how to contact', 'get in touch', 'location'
                ],
                'responses': [
                    "📞 **Contact Information**\n\n"
                    "**Admission Office:** +91 98765 43210\n"
                    "**General Enquiry:** +91 98765 43211\n"
                    "**Email:** info@college.edu\n"
                    "**Website:** www.college.edu\n\n"
                    "**College Address:**\n"
                    "College Road, Education City\n"
                    "State - 400001, India\n\n"
                    "**Office Hours:**\n"
                    "• Monday to Friday: 9:00 AM to 5:00 PM\n"
                    "• Saturday: 9:00 AM to 1:00 PM\n"
                    "• Sunday: Closed"
                ],
                'keywords': ['contact', 'phone', 'email', 'address', 'call', 'reach', 'location']
            },
            'about': {
                'patterns': [
                    'about college', 'college information', 'tell me about college',
                    'college details', 'about this college', 'college overview'
                ],
                'responses': [
                    "🏛️ **About Our College**\n\n"
                    "**Establishment:** 1995\n"
                    "**Campus Size:** 50 acres\n"
                    "**Total Students:** 3,500+\n"
                    "**Faculty:** 200+ qualified teachers\n"
                    "**Courses:** UG, PG, and Doctoral programs\n\n"
                    "**Accreditations:**\n"
                    "• UGC approved\n"
                    "• AICTE recognized\n"
                    "• NAAC A+ grade\n"
                    "• ISO 9001:2015 certified\n\n"
                    "**Rankings:**\n"
                    "• Ranked among top 50 colleges in India\n"
                    "• Best Emerging College Award 2024\n\n"
                    "**Vision:** To be a center of excellence in education, research, and innovation"
                ],
                'keywords': ['about', 'college information', 'overview', 'details']
            }
        }
    
    def preprocess_text(self, text):
        """Advanced text preprocessing with NLTK"""
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def extract_course(self, text):
        """Extract specific course mentioned in query"""
        courses = {
            'bca': ['bca', 'bachelor of computer applications'],
            'mca': ['mca', 'master of computer applications'],
            'mba': ['mba', 'master of business administration'],
            'bsc': ['bsc', 'bachelor of science'],
            'bcom': ['bcom', 'bachelor of commerce']
        }
        
        text_lower = text.lower()
        for course, keywords in courses.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return course
        return None
    
    def get_best_match(self, query):
        """Find the best matching intent using NLP and Fuzzy Matching"""
        query_lower = query.lower()
        processed_query = self.preprocess_text(query)
        query_words = set(word_tokenize(processed_query))
        
        best_intent = None
        best_score = 0
        
        for intent, data in self.knowledge_base.items():
            score = 0
            
            # 1. Pattern Matching (High Weight)
            for pattern in data['patterns']:
                if pattern in query_lower:
                    score += 5  # Increased weight for exact pattern match
                else:
                    # Fuzzy match for pattern
                    match_ratio = SequenceMatcher(None, pattern, query_lower).ratio()
                    if match_ratio > 0.7:
                        score += 3 * match_ratio
            
            # 2. Keyword Matching
            for keyword in data['keywords']:
                if keyword in query_lower:
                    score += 2
                elif any(SequenceMatcher(None, keyword, word).ratio() > 0.8 for word in query_words):
                    score += 1.5
            
            # 3. Contextual word overlap
            common_words = query_words.intersection(set(word_tokenize(" ".join(data['patterns']))))
            score += len(common_words) * 0.5
            
            if score > best_score:
                best_score = score
                best_intent = intent
        
        # Normalize score
        confidence = min(best_score / 6, 1.0)
        return best_intent, confidence
    
    def get_response(self, query, user_id=None):
        """Main method to get chatbot response"""
        start_time = time.time()
        
        # Extract course if mentioned
        course = self.extract_course(query)
        
        # Get best matching intent
        intent, confidence = self.get_best_match(query)
        
        # Check for greetings
        greeting_words = ['hi', 'hello', 'hey', 'namaste', 'good morning', 'good afternoon']
        if any(word in query.lower() for word in greeting_words):
            intent = 'greeting'
            confidence = 1.0
        
        # If no match found
        if not intent or confidence < 0.3:
            response = (
                "I'm not sure I understand. Could you please rephrase your question?\n\n"
                "**You can ask me about:**\n"
                "• Admission process, dates, and eligibility\n"
                "• Course details (BCA, MCA, MBA)\n"
                "• Fee structure\n"
                "• Placement records and companies\n"
                "• Library facilities\n"
                "• Hostel accommodation\n"
                "• Sports and transport facilities\n"
                "• Scholarships and financial aid"
            )
        else:
            response = self.knowledge_base[intent]['responses'][0]
        
        # Analyze sentiment
        blob = TextBlob(query)
        sentiment_score = blob.sentiment.polarity
        if sentiment_score > 0.3:
            sentiment = 'positive'
        elif sentiment_score < -0.3:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        response_time = time.time() - start_time
        
        return {
            'response': response,
            'intent': intent if intent else 'unknown',
            'confidence': confidence,
            'sentiment': sentiment,
            'sentiment_score': sentiment_score,
            'entities': {'course': course} if course else {},
            'response_time': round(response_time, 3)
        }