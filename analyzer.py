import re

def analyze_teamwork_preference(title, description, requirements, responsibilities):
    """
    Analyze if a job is more likely to be done in a team or as an individual.
    
    Returns a float between 0 and 1, where values closer to 1 indicate team work 
    and values closer to 0 indicate individual work.
    """
    if not description:
        description = ""
    if not requirements:
        requirements = ""
    if not responsibilities:
        responsibilities = ""
    
    # Combine all text for analysis
    full_text = f"{title} {description} {requirements} {responsibilities}".lower()
    
    # Team-related keywords (in Latvian and English)
    team_keywords = [
        'team', 'komanda', 'komandā', 'kolektīvs', 'kolektīvā',
        'sadarbība', 'sadarboties', 'collaborate', 'collaboration',
        'grupa', 'grupā', 'koordinēt', 'koordinācija',
        'lead', 'vadīt', 'vadītājs', 'menedžer', 'pārvaldīt',
        'partneri', 'kolēģi', 'colleagues', 'meetings', 'sapulces',
        'pievienojies mūsu komandai', 'join our team', 'komandas darbs',
        'apspriedes', 'sapulces', 'prezentācijas', 'presentations',
        'koordinēšana', 'coordination', 'projektu vadība', 'project management'
    ]
    
    # Individual work keywords
    individual_keywords = [
        'independent', 'neatkarīgi', 'patstāvīgi', 'autonoms',
        'pašmotivēts', 'self-motivated', 'self-directed',
        'individual', 'individuāls', 'remote', 'attālināti',
        'specializēts', 'specialized', 'expert', 'eksperts',
        'autonomi', 'autonomia', 'neatkarība', 'independence',
        'patstāvīgs darbs', 'individual work', 'strādāt patstāvīgi'
    ]
    
    # Count keyword occurrences with word boundary matching to avoid partial matches
    team_count = sum(len(re.findall(r'\b' + re.escape(kw.replace('-', '')) + r'\w*\b', 
                                    full_text.replace('-', ''))) for kw in team_keywords)
    
    individual_count = sum(len(re.findall(r'\b' + re.escape(kw.replace('-', '')) + r'\w*\b', 
                                         full_text.replace('-', ''))) for kw in individual_keywords)
    
    # Additional analysis based on typical job characteristics
    
    # Check for leadership/management roles
    leadership_terms = ['vadītājs', 'manager', 'lead', 'head', 'director', 'chief']
    if any(term in title.lower() for term in leadership_terms):
        team_count += 3
    
    # Customer service roles typically involve team interaction
    if 'klientu apkalpošana' in full_text or 'customer service' in full_text:
        team_count += 2
    
    # Check for team size mentions
    team_size_patterns = [
        r'komanda.{1,30}(\d+).{1,10}(cilvēk|kolēģ|speciālist)',
        r'team of.{1,10}(\d+)',
        r'(\d+).{1,10}(person|people|member) team'
    ]
    
    for pattern in team_size_patterns:
        team_size_match = re.search(pattern, full_text)
        if team_size_match:
            try:
                size = int(team_size_match.group(1))
                if size > 1:
                    team_count += 1
            except:
                pass
    
    # If no keywords found or equal counts, use a more neutral value but slightly biased toward team work
    # since most jobs involve some degree of collaboration
    if team_count + individual_count == 0:
        return 0.55
    
    # Calculate likelihood score (0 to 1)
    return team_count / (team_count + individual_count)

def analyze_learning_opportunity(title, description, requirements, responsibilities):
    """
    Analyze how much learning opportunity a job offers.
    
    Returns a float between 0 and 1, where values closer to 1 indicate high learning opportunity
    and values closer to 0 indicate low learning opportunity.
    """
    if not description:
        description = ""
    if not requirements:
        requirements = ""
    if not responsibilities:
        responsibilities = ""
    
    # Combine all text for analysis
    full_text = f"{title} {description} {requirements} {responsibilities}".lower()
    
    # Learning opportunity keywords
    learning_keywords = [
        'learning', 'growth', 'development', 'training', 'mentor', 'education',
        'mācīties', 'mācības', 'apmācība', 'attīstība', 'izaugsme', 'kursi',
        'sertifikācija', 'certification', 'improve', 'pilnveidot', 'apgūt',
        'profesionālā izaugsme', 'professional growth', 'skills', 'prasmes',
        'paplašināt zināšanas', 'knowledge', 'zināšanas', 'kompetences',
        'jauna tehnoloģija', 'new technology', 'innovation', 'inovācija'
    ]
    
    # Low learning opportunity keywords
    static_keywords = [
        'routine', 'rutīna', 'repetitive', 'atkārtojošs', 'standarta',
        'basic', 'pamata', 'vienkāršs', 'simple', 'monotonous', 'monotons'
    ]
    
    # Count keyword occurrences
    learning_count = sum(len(re.findall(r'\b' + re.escape(kw.replace('-', '')) + r'\w*\b', 
                                       full_text.replace('-', ''))) for kw in learning_keywords)
    
    static_count = sum(len(re.findall(r'\b' + re.escape(kw.replace('-', '')) + r'\w*\b', 
                                     full_text.replace('-', ''))) for kw in static_keywords)
    
    # Check for educational benefits
    if re.search(r'(apmaksā|apmaksāt|cover|pay for).{1,30}(courses|kursi|education|izglītība|studies|training)', full_text):
        learning_count += 3
        
    # If entry level position, likely more to learn
    if re.search(r'(entry.?level|junior|iesācēj|jaunāk)', full_text):
        learning_count += 2
    
    # If senior/lead position, might focus more on applying existing skills
    if re.search(r'(senior|vecāk|lead|vadoš)', title.lower()):
        static_count += 1
    
    # If no keywords found or equal counts, return a neutral value
    if learning_count + static_count == 0:
        return 0.5
    
    # Calculate score (0 to 1)
    return learning_count / (learning_count + static_count)

def analyze_company_size(company, description):
    """
    Estimate company size based on company name and description.
    
    Returns a float between 0 and 1, where values closer to 1 indicate larger companies
    and values closer to 0 indicate smaller companies.
    """
    if not company:
        company = ""
    if not description:
        description = ""
    
    text = f"{company} {description}".lower()
    
    # Check for known large companies in Latvia
    large_companies = [
        'accenture', 'swedbank', 'seb', 'lattelecom', 'tet', 'citadele',
        'maxima', 'rimi', 'lmt', 'bite', 'tele2', 'luminor', 'circle k',
        'latvenergo', 'deloitte', 'ernst & young', 'kpmg', 'pwc', 'microsoft',
        'google', 'amazon', 'ibm', 'oracle', 'sap', 'tietoevry', 'visma'
    ]
    
    # Keywords indicating company size
    large_keywords = [
        'corporation', 'korporācija', 'global', 'globāl', 'international', 
        'starptautisk', 'nasdaq', 'enterprise', 'uzņēmumu grupa', 'group',
        'tūkstošiem darbinieku', 'thousands of employees', 'liels uzņēmums',
        'darbinieki visā pasaulē', 'employees worldwide', 'market leader',
        'tirgus līderis', 'lielākais', 'largest', 'multinational', 'holding'
    ]
    
    small_keywords = [
        'startup', 'jaunuzņēmums', 'small team', 'maza komanda', 'ģimenes uzņēmums',
        'family business', 'boutique', 'niche', 'nišas', 'individuāl', 'mazs uzņēmums'
    ]
    
    # Default medium-small size (0.4)
    size_score = 0.4
    
    # Check for large company indicators
    if any(company.lower() == lc or company.lower().startswith(f"{lc} ") or 
           company.lower().endswith(f" {lc}") or f" {lc} " in company.lower() 
           for lc in large_companies):
        size_score = 0.9
    
    # Count size keywords
    large_count = sum(1 for kw in large_keywords if kw in text)
    small_count = sum(1 for kw in small_keywords if kw in text)
    
    # Adjust score based on keyword counts
    if large_count > small_count:
        size_score = min(size_score + 0.1 * (large_count - small_count), 1.0)
    elif small_count > large_count:
        size_score = max(size_score - 0.1 * (small_count - large_count), 0.0)
    
    # Check for employee count mentions
    employee_match = re.search(r'(\d+)[\s+]*(darbinieku|darbinieki|employees|staff)', text)
    if employee_match:
        try:
            count = int(employee_match.group(1))
            if count < 20:
                size_score = 0.1
            elif count < 50:
                size_score = 0.2
            elif count < 100:
                size_score = 0.3
            elif count < 250:
                size_score = 0.5
            elif count < 500:
                size_score = 0.7
            elif count < 1000:
                size_score = 0.8
            else:
                size_score = 0.9
        except:
            pass
    
    return size_score

def analyze_remote_preference(description, requirements):
    """
    Analyze how remote-friendly a job is.
    
    Returns a float between 0 and 1, where values closer to 1 indicate fully remote
    and values closer to 0 indicate on-site.
    """
    if not description:
        description = ""
    if not requirements:
        requirements = ""
    
    text = f"{description} {requirements}".lower()
    
    # Remote work keywords
    remote_keywords = [
        'remote', 'attālināti', 'work from home', 'strādāt no mājām',
        'remote-first', 'hybrid', 'hibrīd', 'flexible location', 'elastīga darba vieta',
        'home office', 'anywhere', 'jebkur', 'telecommute', 'virtual', 'virtuāl'
    ]
    
    # On-site keywords
    onsite_keywords = [
        'on-site', 'uz vietas', 'office', 'biroj', 'in person', 'klātienē',
        'location', 'lokācij', 'on location', 'darba vietā', 'workplace',
        'attend', 'present', 'klātbūtne'
    ]
    
    # Check for specific phrases
    if re.search(r'(fully|pilnībā|100%).{1,10}(remote|attālināti)', text):
        return 1.0
    
    if re.search(r'(must|jābūt|obligāti|required).{1,20}(office|birojā|klātienē|on.?site|uz vietas)', text):
        return 0.0
        
    if re.search(r'(hybrid|hibrīd).{1,20}(work|darb)', text):
        return 0.5
    
    # Count keyword occurrences
    remote_count = sum(1 for kw in remote_keywords if kw in text)
    onsite_count = sum(1 for kw in onsite_keywords if kw in text)
    
    # If no keywords found, assume moderate on-site preference (0.3)
    if remote_count + onsite_count == 0:
        return 0.3
    
    # Calculate score (0 to 1)
    return remote_count / (remote_count + onsite_count)

def analyze_career_growth(title, description, benefits):
    """
    Analyze career growth opportunities in the job.
    
    Returns a float between 0 and 1, where values closer to 1 indicate high growth potential
    and values closer to 0 indicate limited growth potential.
    """
    if not title:
        title = ""
    if not description:
        description = ""
    if not benefits:
        benefits = ""
    
    text = f"{title} {description} {benefits}".lower()
    
    # Career growth keywords
    growth_keywords = [
        'career', 'karjera', 'promotion', 'paaugstināj', 'advancement', 'izaugsme',
        'growth', 'progress', 'attīstība', 'development', 'mentorship', 'leadership',
        'līderība', 'vadība', 'perspective', 'perspektīva', 'long-term', 'ilgtermiņa',
        'career path', 'karjeras ceļš', 'advance', 'virzīties', 'climb', 'talent program'
    ]
    
    # Limited growth keywords
    limited_keywords = [
        'temporary', 'īslaicīg', 'contract', 'līgumdarbs', 'seasonal', 'sezonas',
        'project-based', 'projekta', 'short-term', 'īstermiņa', 'interim', 'pagaidu'
    ]
    
    # Count keyword occurrences
    growth_count = sum(1 for kw in growth_keywords if kw in text)
    limited_count = sum(1 for kw in limited_keywords if kw in text)
    
    # Management/leadership roles typically have growth paths
    if re.search(r'(manag|vadītāj|vadīt|direct|vad|lead)', title.lower()):
        growth_count += 2
    
    # Entry level positions often have growth potential
    if re.search(r'(trainee|praktikant|intern|stažier|junior|jaunāk)', title.lower()):
        growth_count += 1
    
    # If mentions specific career paths
    if re.search(r'(career|karjeras).{1,15}(path|ceļ|track)', text):
        growth_count += 2
        
    # If promoting from within is mentioned
    if re.search(r'(promot|paaugstina|advance|virzī).{1,20}(within|inside|iekšēji|no iekšienes)', text):
        growth_count += 3
    
    # If no keywords found, return moderate value
    if growth_count + limited_count == 0:
        return 0.5
    
    # Calculate score (0 to 1)
    return growth_count / (growth_count + limited_count)

def analyze_project_type(title, description, responsibilities):
    """
    Analyze what type of projects the job involves.
    
    Returns a float between 0 and 1, where values closer to 0 indicate long-term stable projects
    and values closer to 1 indicate short experimental/innovative projects.
    """
    if not title:
        title = ""
    if not description:
        description = ""
    if not responsibilities:
        responsibilities = ""
    
    text = f"{title} {description} {responsibilities}".lower()
    
    # Long-term project keywords
    long_term_keywords = [
        'maintenance', 'uzturēšana', 'long-term', 'ilgtermiņa', 'stable',
        'stabils', 'ongoing', 'nepārtraukts', 'legacy', 'established', 'iedibināts',
        'support', 'atbalsts', 'sustain', 'uzturēt', 'continuous', 'nepārtraukta',
        'operation', 'operatīv', 'year contract', 'gadu līgums', 'consistent'
    ]
    
    # Short-term/innovative project keywords
    innovative_keywords = [
        'innovative', 'inovatīv', 'startup', 'jaunuzņēmum', 'prototype',
        'prototip', 'pilot', 'experimental', 'eksperimentāl', 'proof of concept',
        'mvp', 'agile', 'scrum', 'sprint', 'rapid', 'ātr', 'dynamic', 'dinamisk',
        'creative', 'radoš', 'cutting-edge', 'jaunāk', 'groundbreaking', 'revolution'
    ]
    
    # Count keyword occurrences
    long_term_count = sum(1 for kw in long_term_keywords if kw in text)
    innovative_count = sum(1 for kw in innovative_keywords if kw in text)
    
    # Maintenance roles tend to be more stable/long-term
    if re.search(r'(mainten|uzturēšan|support|atbalst)', title.lower()):
        long_term_count += 2
    
    # R&D roles tend to be more innovative/short-term
    if re.search(r'(research|pētniec|develop|izstrād|innovat|inovāc)', title.lower()):
        innovative_count += 2
        
    # Check for project duration mentions
    if re.search(r'(short.?term|īstermiņa|quick|temporary|pagaidu)', text):
        innovative_count += 1
        
    if re.search(r'(long.?term|ilgtermiņa|multi.?year|vairāku gadu)', text):
        long_term_count += 1
    
    # If no keywords found, return moderate value
    if long_term_count + innovative_count == 0:
        return 0.5
    
    # Calculate score (0 to 1)
    return innovative_count / (long_term_count + innovative_count)

def analyze_experience_required(title, description, requirements):
    """
    Analyze how much experience is required for the job.
    
    Returns a float between 0 and 1, where values closer to 1 indicate high experience requirements
    and values closer to 0 indicate entry-level positions.
    """
    if not title:
        title = ""
    if not description:
        description = ""
    if not requirements:
        requirements = ""
    
    text = f"{title} {description} {requirements}".lower()
    
    # Entry-level keywords
    entry_keywords = [
        'entry level', 'entry-level', 'junior', 'iesācēj', 'sākuma līmeņa', 
        'no experience', 'bez pieredzes', 'graduate', 'absolvents', 'recent graduate',
        'intern', 'internship', 'praktikants', 'prakse', 'trainee', 'māceklis',
        'assistant', 'asistents'
    ]
    
    # Mid-level keywords
    mid_keywords = [
        'mid level', 'mid-level', 'vidēja līmeņa', 'intermediate', 'experienced', 
        'at least 2 years', 'vismaz 2 gadi', '2+ years', '3+ years', '2-4 years',
        'ar pieredzi', 'with experience', 'pieredze līdzīgā amatā'
    ]
    
    # Senior-level keywords
    senior_keywords = [
        'senior', 'vecākais', 'expert', 'eksperts', 'experienced', 'pieredzējis',
        '5+ years', '5+ gadi', '7+ years', '7+ gadi', '10+ years', '10+ gadi',
        'extensive experience', 'plaša pieredze', 'significant experience', 'lead',
        'vadošais', 'head', 'director', 'direktors'
    ]

    # Check for years of experience with regex
    years_pattern = r'(\d+)(?:\+)?.+?(year|gad|experience|pieredz)'
    years_match = re.search(years_pattern, text)
    
    # Default to mid-level (0.5)
    experience_score = 0.5
    
    # If specific years mentioned, adjust the score
    if years_match:
        try:
            years = int(years_match.group(1))
            if years == 0:
                experience_score = 0.1
            elif years <= 1:
                experience_score = 0.2
            elif years <= 3:
                experience_score = 0.4
            elif years <= 5:
                experience_score = 0.6
            elif years <= 8:
                experience_score = 0.8
            else:
                experience_score = 0.9
        except:
            pass
    else:
        # Count keyword occurrences
        entry_count = sum(1 for kw in entry_keywords if kw in text)
        mid_count = sum(1 for kw in mid_keywords if kw in text)
        senior_count = sum(1 for kw in senior_keywords if kw in text)
        
        # Weight the counts
        weighted_score = (entry_count * 0.2 + mid_count * 0.5 + senior_count * 0.8)
        total_count = entry_count + mid_count + senior_count
        
        # Calculate final score
        if total_count > 0:
            experience_score = weighted_score / total_count
        # If no keywords found, leave as default mid-level
    
    # Additional adjustments based on job title
    if re.search(r'(junior|iesācēj|asistent|praktikant)', title.lower()):
        experience_score = max(experience_score - 0.2, 0.1)
        
    if re.search(r'(senior|vecāk|lead|vadoš|direktors|head)', title.lower()):
        experience_score = min(experience_score + 0.2, 0.9)
    
    return experience_score

def analyze_stress_level(description, responsibilities):
    """
    Analyze the likely stress level of the job.
    
    Returns a float between 0 and 1, where values closer to 1 indicate high-stress jobs
    and values closer to 0 indicate low-stress positions.
    """
    if not description:
        description = ""
    if not responsibilities:
        responsibilities = ""
    
    text = f"{description} {responsibilities}".lower()
    
    # High-stress keywords
    high_stress_keywords = [
        'deadline', 'deadlines', 'termiņi', 'termiņš', 'pressure', 'spiediens',
        'fast-paced', 'ātrs temps', 'high volume', 'liels apjoms', 'stressful',
        'stress', 'emergency', 'ārkārtas', 'urgent', 'steidzams', 'critical',
        'kritiski', 'demanding', 'prasīgs', 'challenging', 'izaicinošs',
        'intense', 'intensīvs', 'high pressure', 'augsts spiediens', 'difficult',
        'overtime', 'virsstundas', 'weekend work', 'darbs brīvdienās', '24/7',
        'on-call', 'dežūras', 'multiple projects', 'vairāki projekti'
    ]
    
    # Low-stress keywords
    low_stress_keywords = [
        'relaxed', 'relaksēts', 'friendly', 'draudzīgs', 'flexible', 'elastīgs',
        'easy-going', 'balanced', 'līdzsvarots', 'work-life balance', 'darba un privātās dzīves līdzsvars',
        'comfortable', 'ērts', 'supportive', 'atbalstošs', 'family-friendly', 'ģimenei draudzīgs',
        'relaxed atmosphere', 'relaksēta atmosfēra', 'no pressure', 'bez spiediena',
        'steady pace', 'mierīgs temps', 'regular hours', 'regulārs darba laiks'
    ]
    
    # Count keyword occurrences
    high_stress_count = sum(1 for kw in high_stress_keywords if kw in text)
    low_stress_count = sum(1 for kw in low_stress_keywords if kw in text)
    
    # Check for multiple deadline mentions (indicates higher stress)
    deadline_matches = len(re.findall(r'deadline|termiņ', text))
    if deadline_matches > 1:
        high_stress_count += deadline_matches
    
    # Check for phrases indicating night shifts or unpredictable hours
    if re.search(r'(night|nakts|shift work|maiņu darbs|unpredictable|neprognozējams|24/7)', text):
        high_stress_count += 2
    
    # Check for mentions of relaxed culture
    if re.search(r'(work.?life.?balance|relax|friendly.?environment|support)', text):
        low_stress_count += 1
    
    # Default to moderate stress level (0.5) if no indicators
    if high_stress_count + low_stress_count == 0:
        return 0.5
    
    # Calculate score (0 to 1)
    return high_stress_count / (high_stress_count + low_stress_count)

def analyze_creativity_required(title, description, responsibilities):
    """
    Analyze how much creativity and innovation is required or valued in the job.
    
    Returns a float between 0 and 1, where values closer to 1 indicate highly creative roles
    and values closer to 0 indicate more process-driven, standard roles.
    """
    if not title:
        title = ""
    if not description:
        description = ""
    if not responsibilities:
        responsibilities = ""
    
    text = f"{title} {description} {responsibilities}".lower()
    
    # Creative role keywords
    creative_keywords = [
        'creative', 'radošs', 'innovation', 'inovācija', 'design', 'dizains',
        'create', 'radīt', 'develop', 'attīstīt', 'new ideas', 'jaunas idejas',
        'brainstorm', 'prāta vētra', 'original', 'oriģināls', 'novel', 'jauns',
        'think outside the box', 'domāt ārpus rāmjiem', 'imagination', 'iztēle',
        'artisti', 'māksliniecisk', 'content creation', 'satura veidošana',
        'solutions', 'risinājumi', 'problem solving', 'problēmu risināšana',
        'initiative', 'iniciatīva', 'concept', 'koncepcija'
    ]
    
    # Process-driven role keywords
    process_keywords = [
        'follow', 'sekot', 'procedure', 'procedūra', 'protocol', 'protokols',
        'standard', 'standarts', 'routine', 'rutīna', 'process', 'process',
        'strict', 'stingrs', 'according to', 'saskaņā ar', 'guidelines', 'vadlīnijas',
        'rules', 'noteikumi', 'regulations', 'regulējumi', 'methodology', 'metodoloģija',
        'step-by-step', 'soli pa solim', 'structured', 'strukturēts'
    ]
    
    # Count keyword occurrences
    creative_count = sum(1 for kw in creative_keywords if kw in text)
    process_count = sum(1 for kw in process_keywords if kw in text)
    
    # Specific creative job roles get a bonus
    creative_roles = [
        'design', 'dizain', 'artist', 'māksliniek', 'creative', 'radoš',
        'content', 'satur', 'writer', 'rakstnie', 'marketing', 'mārketin',
        'ux', 'ui', 'user experience', 'architect', 'arhitekt', 'innovation',
        'r&d', 'research and development', 'pētniec'
    ]
    
    if any(role in title.lower() for role in creative_roles):
        creative_count += 3
    
    # Process/standard roles
    standard_roles = [
        'operator', 'operators', 'clerk', 'assistant', 'asistent',
        'supervisor', 'uzraugs', 'accountant', 'grāmatved', 'compliance',
        'security', 'apsardz', 'maintenance', 'apkop', 'teller', 'kasier'
    ]
    
    if any(role in title.lower() for role in standard_roles):
        process_count += 2
    
    # Check for specific phrases
    if re.search(r'(creative|radoš|innovative|inovatīv).{1,20}(thinking|domāšan|mindset|approach)', text):
        creative_count += 2
    
    if re.search(r'(follow|sekot|adhere to).{1,20}(procedure|procedūr|protocol|protokol)', text):
        process_count += 2
    
    # Default to moderate creativity level (0.5) if no indicators
    if creative_count + process_count == 0:
        return 0.5
    
    # Calculate score (0 to 1)
    return creative_count / (creative_count + process_count)

def analyze_work_environment(teamwork_preference, stress_level, company_size):
    """
    Calculate work environment score from other factors.
    
    Returns a value between 0 and 1, where values closer to 1 indicate a more dynamic, social environment
    and values closer to 0 indicate a more quiet, focused environment.
    """
    # Work environment is influenced by teamwork preference, stress level and company size
    # Higher teamwork = more dynamic environment
    # Higher stress = more active environment 
    # Larger company = more formal environment (negative factor)
    
    dynamic_factor = teamwork_preference * 0.6 + stress_level * 0.4
    formality_factor = company_size * 0.3
    
    # Combine factors with weights
    environment_score = (dynamic_factor * 0.8) - (formality_factor * 0.2)
    
    # Ensure score is between 0 and 1
    return max(0, min(environment_score, 1))
