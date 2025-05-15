import re

def analyze_team_likelihood(title, description, requirements, responsibilities):
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
