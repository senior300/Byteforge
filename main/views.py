import logging

from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import EmailMessage
from django.conf import settings
from django.db import OperationalError, ProgrammingError
from django.db.models import Avg, Count
from .models import Contact, Employee, Rating

logger = logging.getLogger(__name__)

# Service details data
SERVICES = {
    'web-development': {
        'title': 'Web Development',
        'icon': 'fas fa-globe',
        'short_desc': 'Custom websites, e-commerce platforms, responsive design, and CMS integration.',
        'description': 'We build modern, responsive web applications tailored to your business needs. From stunning websites to complex e-commerce platforms, our team delivers solutions that engage users and drive results.',
        'features': [
            'Custom website design & development',
            'E-commerce platforms & shopping carts',
            'Responsive design for all devices',
            'Content Management Systems (CMS)',
            'SEO-optimized architecture',
            'Performance optimization',
            'Security best practices',
            'Ongoing maintenance & support'
        ],
        'technologies': ['React', 'Django', 'Node.js', 'HTML5/CSS3', 'JavaScript', 'PostgreSQL', 'MongoDB'],
        'process': ['Discovery', 'Design', 'Development', 'Testing', 'Deployment', 'Support']
    },
    'mobile-app-development': {
        'title': 'Mobile App Development',
        'icon': 'fas fa-mobile-alt',
        'short_desc': 'iOS and Android apps, cross-platform solutions, UI/UX optimization.',
        'description': 'Create powerful mobile applications that users love. We develop native and cross-platform apps with beautiful interfaces and seamless functionality.',
        'features': [
            'Native iOS & Android development',
            'Cross-platform development',
            'UI/UX optimization',
            'App store deployment',
            'Push notifications',
            'Offline functionality',
            'Real-time synchronization',
            'Advanced analytics integration'
        ],
        'technologies': ['Swift', 'Kotlin', 'React Native', 'Flutter', 'Firebase'],
        'process': ['Strategy', 'Design', 'Development', 'Testing', 'Launch', 'Growth']
    },
    'cybersecurity': {
        'title': 'Cybersecurity',
        'icon': 'fas fa-shield-alt',
        'short_desc': 'Network security, penetration testing, threat analysis, malware protection, and compliance audits.',
        'description': 'Protect your digital assets with comprehensive security solutions. We identify vulnerabilities and implement robust defenses against cyber threats.',
        'features': [
            'Network security assessment',
            'Penetration testing',
            'Vulnerability scanning',
            'Threat analysis & response',
            'Malware protection',
            'Compliance audits (GDPR, HIPAA)',
            'Security training',
            '24/7 monitoring'
        ],
        'technologies': ['Nessus', 'Burp Suite', 'Metasploit', 'Wireshark', 'Splunk'],
        'process': ['Assessment', 'Testing', 'Analysis', 'Remediation', 'Monitoring', 'Reporting']
    },
    'cloud-solutions': {
        'title': 'Cloud Solutions',
        'icon': 'fas fa-server',
        'short_desc': 'Cloud migration, server management, AWS/Azure/Google Cloud deployment, and storage solutions.',
        'description': 'Migrate to the cloud with confidence. We design, deploy, and manage scalable cloud infrastructure for your business.',
        'features': [
            'Cloud migration strategy',
            'AWS, Azure & Google Cloud deployment',
            'Server management & optimization',
            'Auto-scaling infrastructure',
            'Disaster recovery planning',
            'Cost optimization',
            'Cloud security',
            'Backup & storage solutions'
        ],
        'technologies': ['AWS', 'Azure', 'Google Cloud', 'Kubernetes', 'Docker'],
        'process': ['Assessment', 'Planning', 'Migration', 'Optimization', 'Management', 'Support']
    },
    'ai-machine-learning': {
        'title': 'AI & Machine Learning',
        'icon': 'fas fa-robot',
        'short_desc': 'Machine learning models, AI automation, predictive analytics, and intelligent systems development.',
        'description': 'Leverage artificial intelligence to transform your business. We build intelligent systems that automate processes and drive data-driven decisions.',
        'features': [
            'Machine learning model development',
            'Predictive analytics',
            'Natural language processing',
            'Computer vision solutions',
            'AI chatbots & automation',
            'Data analysis & insights',
            'Model training & optimization',
            'Integration with existing systems'
        ],
        'technologies': ['TensorFlow', 'PyTorch', 'Python', 'scikit-learn', 'OpenAI API'],
        'process': ['Data Collection', 'Preparation', 'Model Development', 'Training', 'Evaluation', 'Deployment']
    },
    'data-analysis': {
        'title': 'Data Analysis & BI',
        'icon': 'fas fa-database',
        'short_desc': 'Data visualization, dashboards, business intelligence, and actionable insights.',
        'description': 'Transform raw data into actionable insights. Our BI solutions help you make informed decisions with comprehensive analytics and visualization.',
        'features': [
            'Data warehouse design',
            'Interactive dashboards',
            'Data visualization',
            'Predictive reporting',
            'KPI tracking',
            'Custom analytics',
            'Real-time data processing',
            'Business intelligence strategies'
        ],
        'technologies': ['Tableau', 'Power BI', 'Python', 'SQL', 'Apache Spark'],
        'process': ['Requirements', 'Data Integration', 'Analysis', 'Visualization', 'Reporting', 'Optimization']
    },
    'it-support': {
        'title': 'IT Support & Maintenance',
        'icon': 'fas fa-lock',
        'short_desc': '24/7 system monitoring, troubleshooting, hardware/software support, and managed IT services.',
        'description': 'Keep your systems running smoothly with our proactive IT support. We provide 24/7 monitoring and rapid response to minimize downtime.',
        'features': [
            '24/7 system monitoring',
            'Rapid incident response',
            'Hardware & software support',
            'Network maintenance',
            'System updates & patches',
            'Backup management',
            'User support & training',
            'Remote & on-site assistance'
        ],
        'technologies': ['Windows', 'Linux', 'macOS', 'Networking', 'Virtualization'],
        'process': ['Monitoring', 'Detection', 'Response', 'Resolution', 'Documentation', 'Prevention']
    },
    'networking': {
        'title': 'Networking & Infrastructure',
        'icon': 'fas fa-network-wired',
        'short_desc': 'Network design, LAN/WAN setup, routers, switches, and secure IT infrastructure.',
        'description': 'Build robust network infrastructure that supports your business growth. We design and implement secure, scalable networks.',
        'features': [
            'Network design & planning',
            'LAN/WAN setup & configuration',
            'Router & switch deployment',
            'Network security',
            'Bandwidth optimization',
            'VPN setup',
            'Network monitoring',
            'Infrastructure scaling'
        ],
        'technologies': ['Cisco', 'Juniper', 'Fortinet', 'Palo Alto', 'Arista'],
        'process': ['Assessment', 'Design', 'Implementation', 'Configuration', 'Testing', 'Maintenance']
    },
    'digital-marketing': {
        'title': 'Digital Marketing & SEO',
        'icon': 'fas fa-bullhorn',
        'short_desc': 'SEO optimization, social media strategy, content creation, and digital campaigns.',
        'description': 'Grow your online presence with proven digital marketing strategies. We create campaigns that reach your target audience and drive conversions.',
        'features': [
            'Search engine optimization (SEO)',
            'Social media marketing',
            'Content creation & strategy',
            'Email marketing campaigns',
            'PPC advertising',
            'Influencer partnerships',
            'Analytics & reporting',
            'Brand development'
        ],
        'technologies': ['Google Analytics', 'SEMrush', 'HubSpot', 'Mailchimp', 'Hootsuite'],
        'process': ['Strategy', 'Planning', 'Execution', 'Monitoring', 'Optimization', 'Reporting']
    },
    'software-development': {
        'title': 'Software Development',
        'icon': 'fas fa-cogs',
        'short_desc': 'Custom desktop applications, ERP solutions, SaaS platforms, and system automation.',
        'description': 'Build enterprise-grade software tailored to your unique business needs. From desktop apps to SaaS platforms, we deliver scalable solutions.',
        'features': [
            'Custom desktop applications',
            'Enterprise Resource Planning (ERP)',
            'SaaS platform development',
            'System automation',
            'Legacy system modernization',
            'API development',
            'Database design & optimization',
            'Scalable architecture'
        ],
        'technologies': ['C#', 'Java', 'Python', 'Node.js', 'PostgreSQL', 'Docker'],
        'process': ['Requirements', 'Architecture', 'Development', 'Testing', 'Deployment', 'Maintenance']
    },
    'consulting': {
        'title': 'Consulting & Strategy',
        'icon': 'fas fa-handshake',
        'short_desc': 'IT consulting, digital transformation strategy, and technology roadmap planning.',
        'description': 'Strategic technology guidance for your business. We help you navigate digital transformation and make informed technology decisions.',
        'features': [
            'IT strategy consulting',
            'Digital transformation planning',
            'Technology roadmap development',
            'Process optimization',
            'Change management',
            'Risk assessment',
            'Best practices implementation',
            'Executive training'
        ],
        'technologies': ['Industry Standards', 'ITIL', 'Agile', 'Enterprise Architecture'],
        'process': ['Discovery', 'Analysis', 'Strategy', 'Planning', 'Implementation', 'Review']
    },
    'blockchain': {
        'title': 'Blockchain & Crypto',
        'icon': 'fas fa-link',
        'short_desc': 'Smart contracts, decentralized applications, blockchain integration, and crypto consulting.',
        'description': 'Harness blockchain technology for your business. We develop smart contracts, dApps, and help you navigate the crypto ecosystem.',
        'features': [
            'Smart contract development',
            'Decentralized application (dApp) development',
            'Blockchain integration',
            'Crypto token development',
            'NFT solutions',
            'Consensus mechanism design',
            'Security audits',
            'Blockchain consulting'
        ],
        'technologies': ['Ethereum', 'Solidity', 'Web3.js', 'Truffle', 'Ganache'],
        'process': ['Concept', 'Design', 'Development', 'Testing', 'Audit', 'Deployment']
    }
}

PERFORMANCE = {
    'rating_score': 4.9,
    'rating_count': 136,
    'happy_clients': 128,
    'projects_completed': 89,
    'years_experience': '6',
    'years_label': 'Years of Experience',
    'milestones': [
        {
            'number': '89+',
            'title': 'Projects Completed',
            'description': 'Built end-to-end digital products and platforms for businesses of all sizes.'
        },
        {
            'number': '128+',
            'title': 'Happy Clients',
            'description': 'Trusted by local and international clients for technology, security, and growth.'
        },
        {
            'number': '4.9/5',
            'title': 'Average Rating',
            'description': 'Consistent client satisfaction across web, mobile, cloud, and security projects.'
        }
    ]
}

def home(request):
    employees = Employee.objects.order_by('-created_at')
    rating_stats = Rating.objects.aggregate(avg_rating=Avg('rating'), rating_count=Count('id'))
    average_rating = round(rating_stats['avg_rating'] or 4.9, 1)
    rating_count = rating_stats['rating_count'] or 0
    return render(request, 'main/index.html', {
        'team': employees,
        'performance': PERFORMANCE,
        'milestones': PERFORMANCE['milestones'],
        'rating_summary': {
            'average_rating': average_rating,
            'rating_count': rating_count,
        }
    })

def rate(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        rating_value = request.POST.get('rating')
        comment = request.POST.get('comment')

        if name and email and rating_value:
            try:
                Rating.objects.create(
                    name=name,
                    email=email,
                    rating=int(rating_value),
                    comment=comment or ''
                )
                messages.success(request, 'Thank you for your rating!')
            except Exception as err:
                logger.exception('Failed to save rating')
                messages.error(request, 'Could not save your rating. Please try again.')
        else:
            messages.error(request, 'Please fill in your name, email, and rating.')

    return redirect('/#ratings')

def service_detail(request, service_slug):
    service = SERVICES.get(service_slug)
    if not service:
        return redirect('home')
    return render(request, 'main/service-detail.html', {'service': service, 'service_slug': service_slug, 'all_services': SERVICES})

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        service = request.POST.get('service')
        message_text = request.POST.get('message')
        
        if name and email and phone and service and message_text:
            subject = f'New contact request from {name}'
            message_body = (
                f'Name: {name}\n'
                f'Email: {email}\n'
                f'Phone: {phone}\n'
                f'Service: {service}\n\n'
                f'Message:\n{message_text}'
            )

            try:
                email_message = EmailMessage(
                    subject=subject,
                    body=message_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=settings.CONTACT_RECIPIENTS,
                    reply_to=[email],
                )
                result = email_message.send(fail_silently=False)
                logger.info(f'Contact email sent successfully to {settings.CONTACT_RECIPIENTS}: {result}')
                
                try:
                    Contact.objects.create(
                        name=name,
                        email=email,
                        phone=phone,
                        service=service,
                        message=message_text
                    )
                    logger.info(f'Contact form saved to database: {name}')
                except (OperationalError, ProgrammingError) as db_err:
                    logger.warning(f'Contact saved to email but not database: {db_err}')

                messages.success(request, 'Thank you! Your message has been sent. We will contact you soon.')
            except Exception as err:
                logger.exception(f'Contact form email send failed: {err}')
                if settings.DEBUG:
                    messages.error(request, f'Email send failed: {err}')
                else:
                    messages.error(request, 'Sorry, your message could not be sent right now. Please try again later.')

            return redirect('/#contact')
        else:
            messages.error(request, 'Please fill in all fields.')
            return redirect('/#contact')
    
    return redirect('home')
