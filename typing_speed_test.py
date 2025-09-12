import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import random
import time
import threading
from datetime import datetime
import os

class AdvancedTypingSpeedTest:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Typing Speed Test - 30+ Test Scripts")
        self.root.geometry("1200x800")
        self.root.configure(bg="#2c3e50")
        
        # Variables
        self.current_text = ""
        self.current_text_index = 0
        self.start_time = None
        self.test_active = False
        self.test_duration = 300  # 5 minutes default for longer texts
        self.remaining_time = 300
        self.typed_text = ""
        self.correct_chars = 0
        self.total_chars = 0
        self.errors = 0
        self.auto_complete = False
        
        # 30+ Test texts (200 words each, diverse topics)
        self.test_texts = [
            # Technology & Programming (5 texts)
            """Artificial intelligence represents one of the most transformative technologies of our time, fundamentally changing how we interact with digital systems and process information. Machine learning algorithms can now analyze vast datasets, identify complex patterns, and make predictions with remarkable accuracy. Deep learning neural networks, inspired by the human brain's structure, enable computers to recognize images, understand speech, and even generate creative content. Natural language processing allows machines to comprehend and respond to human communication in increasingly sophisticated ways. Computer vision systems can interpret visual data, enabling applications from autonomous vehicles to medical diagnosis. The Internet of Things connects everyday objects to global networks, creating smart homes, cities, and industrial systems. Cloud computing provides scalable resources on demand, while edge computing brings processing power closer to data sources. Blockchain technology offers secure, decentralized transaction methods that extend far beyond cryptocurrency applications. Quantum computing promises exponential increases in computational power for specific problem types. As these technologies converge, they create unprecedented opportunities for innovation across industries, from healthcare and finance to education and entertainment, reshaping our daily lives in profound ways.""",
            
            """Cybersecurity has become a critical concern as our reliance on digital infrastructure continues to expand exponentially. Sophisticated threat actors employ increasingly complex attack vectors, including advanced persistent threats, zero-day exploits, and social engineering techniques. Organizations must implement comprehensive security frameworks that encompass network protection, endpoint security, data encryption, and user authentication systems. Multi-factor authentication provides additional layers of security beyond traditional password-based systems. Security information and event management platforms help analysts detect and respond to potential threats in real-time. Vulnerability assessment and penetration testing identify weaknesses before malicious actors can exploit them. Security awareness training educates employees about phishing attempts, malware risks, and best practices for maintaining digital hygiene. Incident response procedures ensure rapid containment and recovery from security breaches. Compliance frameworks like GDPR, HIPAA, and SOX mandate specific security controls and data protection measures. Cloud security presents unique challenges as organizations migrate sensitive data and applications to remote servers. The cybersecurity workforce shortage creates additional risks as demand for skilled professionals far exceeds supply, making investment in training and education crucial for organizational resilience.""",
            
            """Software development methodologies have evolved significantly from traditional waterfall approaches to more flexible, iterative frameworks. Agile development emphasizes collaboration, adaptability, and continuous improvement through short development cycles called sprints. Scrum framework provides structured roles, events, and artifacts that facilitate team coordination and project transparency. DevOps practices integrate development and operations teams, enabling faster deployment cycles and improved system reliability. Continuous integration and continuous deployment pipelines automate testing and release processes, reducing human error and accelerating time-to-market. Version control systems like Git enable multiple developers to collaborate effectively on complex codebases while maintaining detailed change histories. Code reviews ensure quality standards and knowledge sharing among team members. Test-driven development encourages writing tests before implementing functionality, resulting in more robust and maintainable code. Microservices architecture breaks applications into small, independent services that can be developed, deployed, and scaled separately. Containerization technologies like Docker provide consistent deployment environments across development, testing, and production systems. These modern practices enable teams to deliver high-quality software more efficiently while adapting to changing requirements and market conditions.""",
            
            """Data science combines statistical analysis, programming skills, and domain expertise to extract meaningful insights from complex datasets. Python and R programming languages provide extensive libraries for data manipulation, visualization, and machine learning implementation. Pandas library enables efficient data cleaning, transformation, and analysis operations on structured datasets. NumPy provides fundamental mathematical operations and array processing capabilities essential for numerical computing. Matplotlib and Seaborn create compelling visualizations that communicate findings to both technical and non-technical audiences. Scikit-learn offers comprehensive machine learning algorithms for classification, regression, clustering, and dimensionality reduction tasks. Deep learning frameworks like TensorFlow and PyTorch enable the development of neural networks for complex pattern recognition problems. SQL databases store and retrieve structured data efficiently, while NoSQL systems handle unstructured and semi-structured information. Big data technologies like Hadoop and Spark process datasets too large for traditional systems. Statistical methods validate hypotheses and quantify uncertainty in analytical results. Feature engineering transforms raw data into formats suitable for machine learning algorithms. Cross-validation techniques ensure model generalization and prevent overfitting. Data scientists must also consider ethical implications, bias detection, and privacy protection when working with sensitive information.""",
            
            """Web development encompasses both front-end and back-end technologies that create interactive, responsive online experiences. HTML provides the structural foundation of web pages, while CSS controls visual presentation and layout design. JavaScript enables dynamic functionality and user interaction through event handling and DOM manipulation. Modern JavaScript frameworks like React, Angular, and Vue.js simplify complex application development through component-based architectures. Node.js allows JavaScript to run on servers, enabling full-stack development with a single programming language. RESTful APIs facilitate communication between different software systems using standard HTTP methods. Database systems store and retrieve application data, with SQL databases providing structured storage and NoSQL options handling flexible schemas. Version control systems track code changes and enable collaborative development among distributed teams. Responsive design techniques ensure websites function properly across desktop computers, tablets, and mobile devices. Progressive web applications combine web and native mobile app features for enhanced user experiences. Content management systems like WordPress democratize website creation for non-technical users. Web security measures protect against common vulnerabilities including cross-site scripting, SQL injection, and cross-site request forgery attacks. Performance optimization techniques improve loading speeds and user satisfaction.""",
            
            # Science & Nature (5 texts)
            """Climate change represents one of the most significant challenges facing humanity in the twenty-first century, with far-reaching consequences for ecosystems, weather patterns, and human societies worldwide. Global average temperatures have risen dramatically since the industrial revolution, primarily due to increased greenhouse gas emissions from fossil fuel combustion, deforestation, and industrial processes. Carbon dioxide concentrations in the atmosphere have reached levels not seen for millions of years, trapping heat and disrupting natural climate systems. Melting polar ice caps contribute to rising sea levels that threaten coastal communities and island nations. Extreme weather events, including hurricanes, droughts, floods, and heat waves, are becoming more frequent and severe. Ocean acidification, caused by absorbed atmospheric carbon dioxide, threatens marine ecosystems and food chains. Arctic permafrost contains vast amounts of methane and carbon dioxide that could accelerate warming if released. Renewable energy technologies like solar, wind, and hydroelectric power offer alternatives to fossil fuels. Energy efficiency improvements in buildings, transportation, and manufacturing can significantly reduce emissions. International cooperation through agreements like the Paris Climate Accord attempts to coordinate global response efforts. Individual actions, from reducing consumption to supporting sustainable practices, contribute to collective climate action.""",
            
            """The human brain contains approximately eighty-six billion neurons that form trillions of synaptic connections, creating the most complex known structure in the universe. Neuroplasticity allows the brain to reorganize and adapt throughout life, forming new neural pathways in response to experiences and learning. Different brain regions specialize in specific functions, from the visual cortex processing sight to the hippocampus forming memories. Neurotransmitters like dopamine, serotonin, and acetylcholine facilitate communication between neurons and influence mood, motivation, and cognitive performance. Sleep plays a crucial role in memory consolidation, toxin removal, and neural maintenance. The blood-brain barrier protects neural tissue from harmful substances while allowing essential nutrients to pass through. Neurological disorders such as Alzheimer's disease, Parkinson's disease, and epilepsy affect millions of people worldwide. Brain imaging technologies like fMRI and PET scans reveal neural activity and structure in living subjects. Cognitive psychology studies how the brain processes information, makes decisions, and forms beliefs. Meditation and mindfulness practices can physically alter brain structure and improve mental health. The gut-brain axis demonstrates how intestinal bacteria influence mood and cognitive function. Ongoing research into consciousness, artificial intelligence, and neural interfaces continues to expand our understanding of this remarkable organ.""",
            
            """Marine ecosystems cover over seventy percent of Earth's surface and contain incredible biodiversity, from microscopic plankton to massive blue whales. Ocean currents distribute heat and nutrients around the globe, influencing weather patterns and supporting complex food webs. Coral reefs, often called rainforests of the sea, provide habitat for approximately twenty-five percent of all marine species despite occupying less than one percent of ocean area. Phytoplankton produce over half of the world's oxygen through photosynthesis while forming the foundation of oceanic food chains. Deep-sea environments harbor unique organisms adapted to extreme pressure, darkness, and cold temperatures. Hydrothermal vents support entire ecosystems independent of sunlight, relying on chemosynthetic bacteria for energy. Overfishing has depleted many fish populations and disrupted marine food webs worldwide. Plastic pollution affects marine life through ingestion, entanglement, and habitat degradation. Ocean acidification, caused by absorbed atmospheric carbon dioxide, threatens shell-forming organisms like corals and mollusks. Marine protected areas help preserve critical habitats and allow overexploited species to recover. Sustainable fishing practices and aquaculture can provide food security while protecting wild populations. Understanding and protecting marine ecosystems is essential for planetary health and human survival.""",
            
            """Genetics and genomics have revolutionized our understanding of heredity, evolution, and human health through detailed analysis of DNA sequences and gene functions. The Human Genome Project mapped all human genetic material, identifying approximately twenty-thousand protein-coding genes and revealing the complex regulatory networks that control gene expression. CRISPR-Cas9 gene editing technology allows precise modifications to DNA sequences, offering potential treatments for genetic diseases and agricultural improvements. Epigenetics studies how environmental factors influence gene activity without changing underlying DNA sequences, explaining how identical twins can develop different traits. Personalized medicine uses genetic information to tailor treatments to individual patients, improving efficacy and reducing adverse reactions. Pharmacogenomics examines how genetic variations affect drug metabolism and response. Population genetics tracks genetic diversity within and between species, informing conservation efforts and evolutionary studies. Genetic counseling helps individuals and families understand hereditary disease risks and make informed reproductive decisions. Gene therapy introduces functional genes to treat or prevent disease, with successful treatments for some previously incurable conditions. Stem cell research explores how undifferentiated cells develop into specialized tissues, potentially enabling regenerative treatments. Ethical considerations surrounding genetic testing, privacy, and enhancement continue to evolve as technology advances. Understanding genetics empowers evidence-based decisions about health, ancestry, and reproduction.""",
            
            """Renewable energy technologies harness naturally replenishing resources to generate electricity and heat while minimizing environmental impact compared to fossil fuels. Solar photovoltaic panels convert sunlight directly into electricity using semiconductor materials, with efficiency improvements and cost reductions making solar power increasingly competitive. Wind turbines capture kinetic energy from moving air masses, with offshore installations accessing stronger, more consistent winds. Hydroelectric systems use flowing or falling water to generate power, providing reliable baseload electricity and energy storage capabilities. Geothermal energy taps into Earth's internal heat for both electricity generation and direct heating applications. Biomass and biofuel production converts organic materials into usable energy while potentially reducing waste streams. Energy storage technologies, including lithium-ion batteries, pumped hydro, and compressed air systems, address the intermittent nature of solar and wind resources. Smart grid systems optimize energy distribution and consumption through real-time monitoring and automated control. Electric vehicles and heat pumps can integrate with renewable energy systems to reduce transportation and heating emissions. Government policies, including tax incentives and renewable portfolio standards, accelerate clean energy adoption. The transition to renewable energy creates jobs in manufacturing, installation, and maintenance while reducing air pollution and greenhouse gas emissions. Continued technological advancement and economic support will determine the pace of global energy transformation.""",
            
            # History & Culture (5 texts)
            """The Renaissance period, spanning roughly from the fourteenth to seventeenth centuries, marked a profound transformation in European culture, art, science, and philosophy. This intellectual and cultural movement began in Italian city-states like Florence, Venice, and Rome before spreading throughout Europe. Humanism emerged as a central philosophy, emphasizing individual potential, classical learning, and secular concerns alongside religious matters. Artists like Leonardo da Vinci, Michelangelo, and Raphael revolutionized painting and sculpture through realistic perspective, anatomical accuracy, and emotional expression. Scientific advancement flourished as scholars challenged medieval assumptions and embraced empirical observation and experimentation. Galileo Galilei's telescopic observations supported heliocentric theory, while Andreas Vesalius corrected centuries of anatomical misconceptions. The printing press, invented by Johannes Gutenberg, democratized knowledge by making books affordable and widely available. Literature experienced a golden age with works by William Shakespeare, Dante Alighieri, and Miguel de Cervantes exploring complex human themes. Architecture incorporated classical Greek and Roman elements while developing new techniques and styles. Banking and commerce expanded, funding artistic patronage and cultural development. The Renaissance laid intellectual foundations for the Scientific Revolution and Enlightenment, fundamentally changing how Europeans viewed themselves and their world, influencing art, science, and philosophy for centuries.""",
            
            """Ancient civilizations in Mesopotamia, Egypt, India, and China independently developed complex societies with sophisticated technologies, governance systems, and cultural achievements that continue to influence modern life. Mesopotamian civilizations invented cuneiform writing, the wheel, and early forms of mathematics and astronomy while establishing the first known legal codes. Ancient Egypt created monumental architecture, advanced medicine, and hieroglyphic writing systems while developing sophisticated agricultural techniques along the Nile River. The Indus Valley Civilization featured planned cities with advanced drainage systems and standardized weights and measures. Ancient China contributed paper, printing, gunpowder, and the compass to global civilization while developing philosophical traditions including Confucianism and Taoism. Greek civilization laid foundations for democracy, philosophy, mathematics, and theater that remain influential today. Roman engineering achievements, including roads, aqueducts, and concrete construction, enabled massive infrastructure projects throughout their empire. These ancient societies developed agriculture, allowing population growth and specialization that enabled cultural and technological advancement. Trade networks connected distant civilizations, facilitating the exchange of goods, ideas, and technologies. Religious and philosophical systems provided social cohesion and meaning while influencing art, literature, and governance. Archaeological discoveries continue to reveal new insights about ancient peoples and their remarkable achievements.""",
            
            """The Industrial Revolution, beginning in eighteenth-century Britain and spreading worldwide, fundamentally transformed human society through mechanization, mass production, and technological innovation. Steam engines revolutionized transportation and manufacturing, powering factories, ships, and railways that connected distant markets and communities. Textile production shifted from household crafts to mechanized factories, dramatically increasing output while changing labor patterns and social structures. Coal mining expanded to fuel steam engines, while iron and steel production enabled construction of machinery, railways, and buildings. Agricultural improvements, including crop rotation and selective breeding, supported growing urban populations engaged in industrial work. Factory systems concentrated workers in industrial centers, creating new social classes and labor relations. Working conditions in early factories were often dangerous and unhealthy, leading to labor organization and reform movements. Urbanization brought both opportunities and challenges as people migrated from rural areas to industrial cities. Transportation improvements, including canals, railways, and steamships, facilitated trade and communication across greater distances. The Industrial Revolution increased productivity and living standards for many while also creating environmental pollution and social inequality. Subsequent waves of industrialization brought electricity, chemical processes, and assembly line production. This transformation established patterns of technological innovation and economic growth that continue to shape modern society.""",
            
            """World War II, lasting from nineteen thirty-nine to nineteen forty-five, stands as the most devastating conflict in human history, involving over thirty countries and resulting in an estimated seventy million casualties worldwide. The war began when Nazi Germany invaded Poland, prompting Britain and France to declare war on Germany. Adolf Hitler's aggressive expansion across Europe included the occupation of France, Norway, Belgium, and the Netherlands. The Holocaust systematically murdered six million Jewish people along with millions of others deemed undesirable by the Nazi regime. The Soviet Union initially allied with Germany but became a crucial Allied power after Germany's invasion in nineteen forty-one. Japan's attack on Pearl Harbor in December nineteen forty-one brought the United States fully into the conflict. Major battles included Stalingrad, D-Day, Midway, and Guadalcanal, each marking turning points in the war's progression. The development and use of atomic weapons on Hiroshima and Nagasaki demonstrated unprecedented destructive capability. Women entered the workforce in unprecedented numbers while men served in military forces worldwide. The war accelerated technological development in aviation, radar, computers, and medicine. Post-war consequences included the emergence of the United States and Soviet Union as superpowers, the beginning of the Cold War, and the establishment of the United Nations to prevent future global conflicts.""",
            
            """Cultural diversity encompasses the vast array of human traditions, languages, beliefs, and practices that have developed across different societies throughout history. Language represents one of the most fundamental aspects of culture, with over seven thousand languages spoken worldwide, each encoding unique worldviews and knowledge systems. Traditional music, dance, and artistic expressions reflect cultural values while providing entertainment and social cohesion within communities. Cuisine traditions incorporate local ingredients, cooking techniques, and social customs that define cultural identity and bring people together. Religious and spiritual practices vary enormously across cultures, offering different perspectives on existence, morality, and the afterlife. Family structures, gender roles, and social hierarchies differ significantly between societies, influencing individual behavior and community organization. Festivals and celebrations mark important seasonal, religious, or historical events while strengthening cultural bonds and traditions. Globalization has increased cultural exchange while also threatening the survival of minority cultures and indigenous knowledge systems. Cultural preservation efforts include documenting languages, protecting traditional arts, and supporting indigenous communities. Education about cultural diversity promotes understanding and reduces prejudice between different groups. Immigration and urbanization create multicultural societies where different traditions can coexist and influence each other. Respecting cultural diversity enriches human experience while contributing to creativity, innovation, and social harmony in increasingly interconnected communities.""",
            
            # Literature & Arts (5 texts)
            """Literature serves as a powerful medium for exploring human experiences, emotions, and ideas across cultures and time periods, offering insights into both individual psychology and societal conditions. Classic works by authors like William Shakespeare, Jane Austen, and Charles Dickens continue to resonate with readers centuries after their creation due to their universal themes and masterful storytelling. Poetry distills complex emotions and observations into concentrated language that can evoke powerful responses and lasting memories. Modern literature encompasses diverse voices and perspectives, including authors from previously marginalized communities who contribute unique narratives and viewpoints. Science fiction and fantasy genres explore possibilities beyond current reality while often commenting on contemporary social and technological issues. Mystery and thriller novels engage readers through suspenseful plots and psychological complexity. Young adult literature addresses coming-of-age themes while tackling serious social issues relevant to adolescent readers. Graphic novels and comic books combine visual and textual storytelling to create immersive narrative experiences. Digital publishing has democratized literature creation and distribution while changing reading habits and accessibility. Literary criticism and analysis help readers understand deeper meanings, historical contexts, and artistic techniques used by authors. Translation makes literature accessible across language barriers while preserving cultural nuances and artistic integrity. Reading literature develops empathy, critical thinking skills, and cultural awareness while providing entertainment and intellectual stimulation.""",
            
            """Visual arts encompass painting, sculpture, photography, and digital media that communicate ideas, emotions, and experiences through aesthetic expression and creative composition. Painting techniques have evolved from ancient cave art to contemporary abstract expressionism, with artists using color, form, and texture to convey meaning. Renaissance masters like Leonardo da Vinci and Michelangelo established principles of perspective, proportion, and realistic representation that influenced centuries of artistic development. Impressionism revolutionized art by emphasizing light, color, and immediate visual impressions rather than detailed realistic representation. Modern art movements including Cubism, Surrealism, and Abstract Expressionism challenged traditional conventions and explored new forms of creative expression. Sculpture transforms raw materials like stone, metal, and clay into three-dimensional artworks that occupy and interact with physical space. Photography captures moments in time while also serving as an artistic medium through composition, lighting, and post-processing techniques. Digital art and computer graphics have created entirely new possibilities for creative expression and commercial application. Street art and murals bring artistic expression to public spaces while often addressing social and political issues. Art therapy uses creative processes to promote healing and emotional well-being. Museums and galleries preserve artistic heritage while making art accessible to diverse audiences. Art education develops creativity, visual literacy, and cultural appreciation while supporting the next generation of artists and art enthusiasts.""",
            
            """Theater represents one of the oldest forms of storytelling and entertainment, combining acting, writing, music, and visual design to create live performances that engage audiences emotionally and intellectually. Ancient Greek theater established many conventions still used today, including dramatic structure, chorus functions, and the use of masks to convey character types. William Shakespeare's plays demonstrate the power of theater to explore complex human psychology and universal themes through memorable characters and poetic language. Musical theater combines songs, dance, and dialogue to tell stories through multiple artistic mediums, creating emotionally powerful and entertaining experiences. Method acting techniques encourage performers to draw upon personal experiences and emotions to create authentic and compelling character portrayals. Stage design includes sets, lighting, costumes, and sound effects that establish mood, location, and atmosphere while supporting the narrative. Community theater provides opportunities for amateur performers while bringing live entertainment to local audiences. Experimental theater challenges conventional forms and explores new ways of engaging audiences and expressing ideas. Theater education develops communication skills, confidence, and creativity while teaching collaboration and artistic appreciation. The COVID-19 pandemic forced theaters to explore virtual and hybrid performance formats, demonstrating the adaptability of live performance. Theater continues to address contemporary social issues while preserving classical works that remain relevant to modern audiences. Live performance creates unique, unrepeatable experiences that connect performers and audiences in ways that recorded media cannot match.""",
            
            """Music represents a universal language that transcends cultural boundaries while expressing emotions, telling stories, and bringing people together through shared rhythmic and melodic experiences. Classical music traditions from various cultures have developed sophisticated compositions that continue to be performed and appreciated centuries after their creation. Popular music genres including rock, jazz, hip-hop, and electronic dance music reflect contemporary culture while influencing fashion, language, and social movements. Musical instruments from different cultures produce unique timbres and playing techniques that contribute to diverse musical expressions worldwide. Music education develops listening skills, discipline, and creativity while providing students with lifelong appreciation and performance abilities. Digital technology has revolutionized music production, distribution, and consumption, making music creation more accessible while changing industry economics. Live concerts and festivals create communal experiences that strengthen social bonds and support local economies. Music therapy uses sound and rhythm to promote healing, reduce stress, and improve quality of life for people with various conditions. Streaming platforms have made vast musical libraries instantly accessible while raising questions about artist compensation and music discovery algorithms. Folk music traditions preserve cultural heritage and historical narratives through songs passed down through generations. Collaboration between musicians from different backgrounds creates fusion genres that blend traditional and contemporary elements. Music continues to evolve through technological innovation while maintaining its fundamental power to move, inspire, and unite people across all demographics and cultures.""",
            
            """Architecture combines artistic vision with engineering principles to create functional and aesthetically pleasing structures that shape human environments and experiences. Ancient architectural marvels like the Pyramids of Giza, Parthenon, and Roman Colosseum demonstrate the enduring power of thoughtful design and skilled construction. Gothic cathedrals showcased innovative engineering techniques including flying buttresses and ribbed vaults while creating spaces that inspired spiritual contemplation. Modern architecture movements like Bauhaus emphasized functional design and industrial materials while rejecting ornate traditional styles. Sustainable architecture incorporates environmental considerations including energy efficiency, renewable materials, and minimal ecological impact. Urban planning determines how buildings relate to each other and to transportation, green spaces, and infrastructure systems. Architectural preservation protects historically significant structures while adapting them for contemporary use and accessibility requirements. Digital design tools enable architects to visualize complex structures and test performance before construction begins. Green building standards promote environmentally responsible construction practices and long-term sustainability. Universal design principles ensure that buildings are accessible to people with varying physical abilities and needs. Architectural education combines artistic creativity with technical knowledge of materials, structural systems, and building codes. Cultural architecture reflects local traditions, climate conditions, and available materials while expressing community values and identity. Thoughtful architecture can improve quality of life, promote social interaction, and create inspiring spaces that enhance human experiences and community well-being.""",
            
            # Business & Economics (5 texts)
            """Entrepreneurship drives economic growth and innovation by creating new businesses, products, and services that meet evolving market needs while generating employment opportunities and wealth creation. Successful entrepreneurs identify unmet consumer needs or inefficiencies in existing markets and develop creative solutions through products or services. Business planning involves market research, financial projections, competitive analysis, and strategic development to guide startup formation and growth. Venture capital and angel investors provide funding for promising startups in exchange for equity stakes and potential returns on investment. Technology startups have created entirely new industries and disrupted traditional business models through innovation and scalability. Small businesses form the backbone of many economies, providing local employment and serving community needs while contributing to economic diversity. Social entrepreneurship addresses social and environmental problems through sustainable business models that create both profit and positive impact. E-commerce platforms have democratized retail by allowing small businesses to reach global customers without significant upfront investment in physical infrastructure. Innovation requires creativity, risk-taking, and persistence to overcome obstacles and bring new ideas to market successfully. Lean startup methodology emphasizes rapid prototyping, customer feedback, and iterative improvement to minimize waste and maximize learning. Failure is an inherent part of entrepreneurship, providing valuable lessons and experience for future ventures. Government policies including tax incentives, regulatory frameworks, and support programs can encourage or hinder entrepreneurial activity and small business development.""",
            
            """Global economics examines how countries trade goods and services while managing monetary systems, exchange rates, and international economic relationships that affect billions of people worldwide. International trade allows countries to specialize in producing goods and services where they have comparative advantages, increasing overall efficiency and consumer choice. Currency exchange rates fluctuate based on economic conditions, political stability, and market confidence, affecting the cost of international transactions and travel. Globalization has increased economic interdependence while creating both opportunities for growth and vulnerabilities to economic disruption. Supply chains now span multiple countries, creating efficiency but also potential risks during crises like natural disasters or pandemics. Economic development varies dramatically between countries, with some achieving high living standards while others struggle with poverty and limited opportunities. International organizations like the World Bank and International Monetary Fund provide financial assistance and policy guidance to developing countries. Trade agreements and economic unions facilitate commerce while sometimes creating disputes over labor standards, environmental protection, and national sovereignty. Economic inequality both within and between countries has become a significant political and social issue requiring policy attention. Technological advancement and automation affect employment patterns and wage levels across different industries and skill categories. Climate change poses economic risks through extreme weather events, resource scarcity, and necessary transitions to sustainable energy systems. Understanding global economics helps individuals and policymakers make informed decisions about trade, investment, and development strategies.""",
            
            """Marketing and consumer behavior analysis helps businesses understand how people make purchasing decisions and develop strategies to reach target audiences effectively while building brand loyalty and driving sales growth. Market research employs surveys, focus groups, and data analysis to identify consumer preferences, needs, and purchasing patterns across different demographic segments. Digital marketing leverages social media, search engines, and online platforms to reach consumers with targeted messages based on their interests and behaviors. Brand development creates distinctive identities that differentiate products and services while building emotional connections with customers through consistent messaging and experiences. Content marketing provides valuable information and entertainment to potential customers, establishing trust and expertise while subtly promoting products or services. Customer relationship management systems track interactions and preferences to enable personalized communication and improve customer satisfaction and retention rates. Pricing strategies balance profitability with market competitiveness while considering consumer psychology and perceived value of products or services. Advertising campaigns use creative messaging and strategic media placement to raise awareness, influence attitudes, and motivate purchasing behavior among target audiences. Social media influencers and word-of-mouth marketing leverage personal recommendations and social proof to build credibility and reach new customer segments. Marketing ethics considerations include truthful advertising, consumer privacy protection, and responsible targeting of vulnerable populations. Measuring marketing effectiveness through analytics and key performance indicators helps businesses optimize their strategies and budget allocation. Understanding marketing principles helps consumers make informed decisions while appreciating the techniques used to influence their behavior.""",
            
            """Financial literacy encompasses understanding money management, investing, credit, insurance, and retirement planning skills that enable individuals to make informed decisions about their economic well-being throughout their lives. Budgeting involves tracking income and expenses to ensure spending aligns with priorities and financial goals while avoiding debt and building savings for future needs. Emergency funds provide financial security by covering unexpected expenses like medical bills, car repairs, or job loss without requiring high-interest debt. Credit scores and credit reports affect access to loans, mortgages, and even employment opportunities, making responsible credit management crucial for financial success. Investment options including stocks, bonds, mutual funds, and real estate offer different risk-return profiles for building wealth over time through compound growth. Retirement planning requires understanding employer-sponsored plans, individual retirement accounts, and social security benefits to ensure adequate income during non-working years. Insurance products protect against financial losses from accidents, illness, disability, or death, providing peace of mind and financial security for individuals and families. Tax planning strategies can minimize tax liability while maximizing after-tax income through deductions, credits, and timing of income and expenses. Debt management involves understanding interest rates, repayment strategies, and the long-term costs of borrowing money for education, housing, or consumer purchases. Financial scams and predatory lending practices target vulnerable individuals, making education about warning signs and protective measures essential. Economic factors including inflation, recession, and market volatility affect personal finances and require adaptive planning strategies. Developing financial literacy early in life establishes foundation for lifelong economic security and independence.""",
            
            """Supply chain management coordinates the flow of goods, information, and finances from raw material suppliers through manufacturers, distributors, and retailers to end consumers efficiently and cost-effectively. Just-in-time inventory systems minimize storage costs by coordinating production and delivery schedules to reduce waste and improve efficiency. Logistics involves transportation, warehousing, and distribution network optimization to move products from producers to consumers quickly and economically. Quality control systems ensure that products meet specifications and safety standards throughout the manufacturing and distribution process. Supplier relationship management builds partnerships that improve communication, reduce costs, and ensure reliable delivery of materials and components. Technology integration including RFID tracking, automated systems, and data analytics improves visibility and control throughout supply chain operations. Risk management identifies potential disruptions including natural disasters, political instability, and supplier failures while developing contingency plans to maintain operations. Sustainability initiatives focus on reducing environmental impact through efficient transportation, responsible sourcing, and waste reduction throughout supply chains. Global supply chains offer cost advantages but create complexity and vulnerability to international disruptions and regulatory changes. E-commerce has transformed distribution requirements by increasing direct-to-consumer shipping while raising customer expectations for fast delivery. Lean manufacturing principles eliminate waste and improve efficiency by focusing on value-added activities and continuous improvement processes. Understanding supply chain principles helps consumers appreciate the complexity behind product availability while supporting businesses that operate ethically and sustainably.""",
            
            # Health & Fitness (3 texts)
            """Physical fitness encompasses cardiovascular endurance, muscular strength, flexibility, and body composition that contribute to overall health and quality of life throughout all stages of human development. Regular exercise provides numerous benefits including reduced risk of chronic diseases like heart disease, diabetes, and osteoporosis while improving mental health and cognitive function. Cardiovascular activities like running, cycling, and swimming strengthen the heart and lungs while improving circulation and endurance for daily activities and recreational pursuits. Strength training builds muscle mass and bone density while improving metabolism and functional capacity for lifting, carrying, and performing everyday tasks safely. Flexibility and mobility exercises maintain joint range of motion and prevent injury while reducing muscle tension and improving posture and movement quality. Proper nutrition supports fitness goals by providing energy for exercise and nutrients for muscle recovery and adaptation to training stimuli. Sleep quality and duration affect exercise performance and recovery while supporting immune function and hormone regulation essential for optimal health. Progressive overload principles guide exercise program design by gradually increasing intensity, duration, or frequency to promote continuous improvement and adaptation. Individual differences in genetics, age, fitness level, and health status require personalized exercise prescriptions to maximize benefits while minimizing injury risk. Group fitness classes and team sports provide social interaction and motivation while making exercise more enjoyable and sustainable for many people. Technology including fitness trackers and smartphone apps can monitor progress and provide feedback to support exercise adherence and goal achievement.""",
            
            """Nutrition science examines how food and beverages affect human health, growth, and performance through the study of macro and micronutrients, digestion, metabolism, and dietary patterns across populations. Macronutrients including carbohydrates, proteins, and fats provide energy and building blocks for cellular function while supporting growth, repair, and maintenance of body tissues. Vitamins and minerals serve as cofactors in biochemical processes essential for immune function, bone health, blood formation, and energy metabolism throughout the body. Hydration maintains cellular function, temperature regulation, and nutrient transport while supporting kidney function and preventing dehydration-related performance decrements. Dietary fiber promotes digestive health, blood sugar regulation, and cardiovascular health while supporting beneficial gut bacteria that influence immune function and mood. Food safety practices prevent foodborne illness through proper handling, cooking, and storage of perishable items while understanding expiration dates and contamination risks. Meal planning and preparation support healthy eating goals by ensuring adequate nutrition while managing time, budget, and convenience factors that affect food choices. Special dietary needs including food allergies, intolerances, and medical conditions require modified eating plans developed with healthcare professional guidance. Sustainable food systems consider environmental impact, animal welfare, and social justice issues related to food production, distribution, and consumption patterns. Reading nutrition labels helps consumers make informed choices about processed foods while understanding serving sizes, ingredient lists, and nutrient content. Cultural food traditions provide social connection and identity while contributing to dietary diversity and culinary heritage that can be incorporated into healthy eating patterns.""",
            
            """Mental health encompasses emotional, psychological, and social well-being that affects how people think, feel, and act while influencing their ability to handle stress, relate to others, and make decisions throughout life. Common mental health conditions including depression, anxiety, and bipolar disorder affect millions of people worldwide while being highly treatable with appropriate professional intervention and support. Stress management techniques including deep breathing, meditation, and time management help individuals cope with daily pressures while building resilience and preventing burnout. Social connections and support networks provide emotional resources and practical assistance during difficult times while contributing to overall life satisfaction and mental wellness. Therapy and counseling offer professional support for addressing mental health challenges through various approaches including cognitive-behavioral therapy, mindfulness-based interventions, and family therapy. Lifestyle factors including regular exercise, adequate sleep, healthy nutrition, and meaningful activities contribute significantly to mental health and emotional well-being. Substance abuse often co-occurs with mental health conditions and requires integrated treatment addressing both issues simultaneously for optimal outcomes. Mental health stigma prevents many people from seeking help, making education and awareness campaigns essential for promoting treatment and recovery. Crisis intervention services provide immediate support for individuals experiencing mental health emergencies while connecting them to longer-term resources and care. Workplace mental health programs support employee well-being while reducing absenteeism and improving productivity through stress reduction and support services. Mental health first aid training teaches community members to recognize warning signs and provide initial support while connecting individuals to professional resources and care.""",
            
            # Travel & Geography (2 texts)
            """Geography encompasses the study of Earth's physical features, climate patterns, natural resources, and human societies, examining how these elements interact to shape our planet's diverse landscapes and cultures. Physical geography examines landforms, weather systems, ecosystems, and natural processes that create mountains, rivers, deserts, and oceans while influencing where and how people live. Human geography analyzes population distribution, urbanization, economic activities, and cultural practices that vary across different regions and countries worldwide. Climate zones from tropical rainforests to arctic tundra support different plant and animal species while influencing human activities including agriculture, housing, and transportation systems. Natural resources including water, minerals, forests, and fossil fuels affect economic development while creating both opportunities and conflicts between nations and communities. Cartography and geographic information systems enable accurate mapping and spatial analysis for urban planning, environmental monitoring, and navigation purposes. Migration patterns throughout history have shaped cultural diversity, economic opportunities, and political boundaries while continuing to influence contemporary societies. Environmental challenges including climate change, deforestation, and pollution require understanding of geographic systems and international cooperation for effective solutions. Tourism industry relies on geographic attractions including natural wonders, historical sites, and cultural destinations while contributing to economic development and cultural exchange. Globalization has increased connections between distant places while also highlighting geographic inequalities in resources, opportunities, and living standards. Understanding geography helps people appreciate Earth's diversity while making informed decisions about travel, conservation, and global citizenship responsibilities.""",
            
            """International travel broadens perspectives by exposing travelers to different cultures, languages, and ways of life while creating opportunities for personal growth and global understanding. Planning successful trips involves researching destinations, understanding visa requirements, booking transportation and accommodation, and preparing for different climates and cultural norms. Budget travel strategies including hostels, public transportation, and local dining help make international experiences accessible while supporting local economies and authentic cultural interactions. Language skills enhance travel experiences by enabling deeper communication with local people while demonstrating respect for host cultures and facilitating navigation and problem-solving. Cultural sensitivity and awareness help travelers navigate differences in customs, etiquette, and social norms while avoiding misunderstandings and showing respect for local traditions. Travel safety requires awareness of local conditions, health precautions, and emergency procedures while maintaining situational awareness and protecting personal belongings and documents. Sustainable tourism practices minimize environmental impact while supporting local communities through responsible spending and cultural appreciation rather than exploitation. Travel photography and journaling preserve memories while sharing experiences with others and documenting cultural diversity and natural beauty. Solo travel builds independence and confidence while offering opportunities for self-reflection and personal challenge outside familiar environments. Group travel and guided tours provide social interaction and expert knowledge while reducing planning stress and increasing safety in unfamiliar destinations. Technology including translation apps, navigation tools, and booking platforms has made travel planning and execution more accessible while maintaining the adventure and unpredictability that make travel rewarding.""",
            
            # Environment & Sustainability (3 texts)
            """Environmental conservation protects natural ecosystems, biodiversity, and resources through sustainable practices that balance human needs with ecological health for current and future generations. Biodiversity conservation preserves the variety of plant and animal species that maintain ecosystem stability while providing resources for medicine, food, and other human needs. Protected areas including national parks, wildlife refuges, and marine reserves provide safe habitats for endangered species while offering opportunities for education and recreation. Renewable resource management ensures sustainable use of forests, fisheries, and water supplies while maintaining ecosystem services and preventing overexploitation. Pollution control measures reduce contamination of air, water, and soil through regulation, technology, and behavior change that protects both human health and environmental quality. Habitat restoration projects repair damaged ecosystems while creating opportunities for species recovery and improved environmental services like water filtration and carbon storage. Climate change mitigation requires reducing greenhouse gas emissions through energy efficiency, renewable energy, and sustainable transportation while adapting to changing conditions. Recycling and waste reduction minimize resource consumption while reducing landfill waste and pollution that threaten environmental and human health. Environmental education increases awareness and knowledge about ecological systems while encouraging responsible behavior and support for conservation policies. Green technology development creates innovations that reduce environmental impact while maintaining economic productivity and quality of life. Individual actions including energy conservation, sustainable consumption, and outdoor recreation support broader conservation goals while connecting people to natural environments. Understanding environmental issues empowers citizens to make informed choices about lifestyle, consumption, and political support for policies that protect planetary health.""",
            
            """Sustainable development aims to meet present needs without compromising future generations' ability to meet their own needs through economic growth that protects environmental quality and social equity. Circular economy principles minimize waste by designing products for reuse, recycling, and regeneration while creating closed-loop systems that eliminate disposal and pollution. Green building design incorporates energy efficiency, renewable materials, and environmental considerations to reduce resource consumption while creating healthy indoor environments for occupants. Sustainable agriculture practices maintain soil health and biodiversity while producing food efficiently without depleting natural resources or causing environmental degradation. Renewable energy systems including solar, wind, and geothermal power provide clean electricity while reducing dependence on fossil fuels and greenhouse gas emissions. Water conservation and management protect this vital resource through efficient use, pollution prevention, and sustainable infrastructure that serves growing populations. Transportation sustainability includes public transit, electric vehicles, active transportation, and urban planning that reduces emissions while improving mobility and quality of life. Corporate social responsibility encourages businesses to consider environmental and social impacts alongside profit while implementing sustainable practices throughout their operations. International cooperation through agreements and organizations addresses global environmental challenges that cross national boundaries and require coordinated responses. Life cycle assessment evaluates environmental impacts of products and services from resource extraction through disposal to identify opportunities for improvement. Sustainable consumption choices by individuals and communities support businesses and practices that minimize environmental impact while meeting human needs. Education about sustainability principles empowers people to make informed decisions that contribute to long-term environmental and social well-being.""",
            
            """Ecosystem services provide essential benefits that natural systems offer to human societies, including clean air and water, climate regulation, food production, and recreational opportunities worth trillions of dollars annually. Forests provide timber, paper, and non-timber products while storing carbon, preventing soil erosion, regulating water cycles, and supporting biodiversity that maintains ecological balance. Wetlands filter pollutants from water while providing flood control, storm protection, and habitat for fish and wildlife that support both ecological health and economic activities. Pollinators including bees, butterflies, and other insects enable fruit and seed production for both wild plants and agricultural crops essential for food security worldwide. Soil formation and nutrient cycling support agriculture and natural plant growth while carbon storage in soils helps regulate atmospheric greenhouse gas concentrations. Ocean ecosystems provide fish and other seafood while regulating climate through heat and carbon dioxide absorption and generating oxygen through marine photosynthesis. Natural pest control by predators and parasites reduces crop damage while maintaining ecological balance without synthetic pesticides that may harm beneficial species. Genetic diversity in wild species provides raw material for developing new medicines, crop varieties, and other products that benefit human health and welfare. Recreational and cultural services including hiking, wildlife viewing, and spiritual connections to nature contribute to human well-being and quality of life. Economic valuation of ecosystem services helps decision-makers understand the true costs of environmental degradation while demonstrating the value of conservation investments. Protecting and restoring natural ecosystems maintains these vital services while supporting both environmental health and human prosperity for current and future generations."""
        ]
        
        # Statistics
        self.test_history = []
        self.load_history()
        
        self.create_widgets()
        self.select_new_text()
        
    def create_widgets(self):
        # Title
        title_frame = tk.Frame(self.root, bg="#2c3e50")
        title_frame.pack(pady=20)
        
        title_label = tk.Label(title_frame, text="⚡ Advanced Typing Speed Test - 30+ Scripts ⚡", 
                              font=("Arial", 24, "bold"), fg="#ecf0f1", bg="#2c3e50")
        title_label.pack()
        
        # Settings frame
        settings_frame = tk.Frame(self.root, bg="#34495e", relief=tk.RAISED, bd=2)
        settings_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(settings_frame, text="Test Mode:", font=("Arial", 12), 
                fg="#ecf0f1", bg="#34495e").pack(side=tk.LEFT, padx=10)
        
        self.mode_var = tk.StringVar(value="Complete Text")
        mode_combo = ttk.Combobox(settings_frame, textvariable=self.mode_var, 
                                 values=["Complete Text", "60 seconds", "120 seconds", "300 seconds"], 
                                 state="readonly", width=15)
        mode_combo.pack(side=tk.LEFT, padx=5)
        mode_combo.bind("<<ComboboxSelected>>", self.change_mode)
        
        tk.Label(settings_frame, text="Current Text:", font=("Arial", 12), 
                fg="#ecf0f1", bg="#34495e").pack(side=tk.LEFT, padx=(30, 5))
        
        self.text_info_label = tk.Label(settings_frame, text="Text 1/30 (Technology)", 
                                       font=("Arial", 12, "bold"), fg="#3498db", bg="#34495e")
        self.text_info_label.pack(side=tk.LEFT, padx=5)
        
        # Statistics display
        stats_frame = tk.Frame(self.root, bg="#2c3e50")
        stats_frame.pack(pady=10)
        
        self.wpm_label = tk.Label(stats_frame, text="WPM: 0", font=("Arial", 16, "bold"), 
                                 fg="#3498db", bg="#2c3e50")
        self.wpm_label.pack(side=tk.LEFT, padx=20)
        
        self.accuracy_label = tk.Label(stats_frame, text="Accuracy: 100%", font=("Arial", 16, "bold"), 
                                      fg="#27ae60", bg="#2c3e50")
        self.accuracy_label.pack(side=tk.LEFT, padx=20)
        
        self.progress_label = tk.Label(stats_frame, text="Progress: 0%", font=("Arial", 16, "bold"), 
                                     fg="#9b59b6", bg="#2c3e50")
        self.progress_label.pack(side=tk.LEFT, padx=20)
        
        self.time_label = tk.Label(stats_frame, text="Time: --", font=("Arial", 16, "bold"), 
                                  fg="#e74c3c", bg="#2c3e50")
        self.time_label.pack(side=tk.LEFT, padx=20)
        
        self.errors_label = tk.Label(stats_frame, text="Errors: 0", font=("Arial", 16, "bold"), 
                                    fg="#f39c12", bg="#2c3e50")
        self.errors_label.pack(side=tk.LEFT, padx=20)
        
        # Text display frame
        text_frame = tk.Frame(self.root, bg="#34495e", relief=tk.RAISED, bd=3)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Scrollable text display
        text_scroll_frame = tk.Frame(text_frame, bg="#34495e")
        text_scroll_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.text_display = tk.Text(text_scroll_frame, height=10, font=("Courier", 12), 
                                   wrap=tk.WORD, bg="#ecf0f1", fg="#2c3e50", 
                                   state=tk.DISABLED, relief=tk.FLAT, bd=10)
        
        text_scrollbar = ttk.Scrollbar(text_scroll_frame, orient=tk.VERTICAL, command=self.text_display.yview)
        self.text_display.configure(yscrollcommand=text_scrollbar.set)
        
        self.text_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Input area
        input_frame = tk.Frame(self.root, bg="#2c3e50")
        input_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(input_frame, text="Type here:", font=("Arial", 14, "bold"), 
                fg="#ecf0f1", bg="#2c3e50").pack(anchor=tk.W)
        
        input_scroll_frame = tk.Frame(input_frame, bg="#2c3e50")
        input_scroll_frame.pack(fill=tk.X, pady=5)
        
        self.input_text = tk.Text(input_scroll_frame, height=5, font=("Courier", 12), 
                                 wrap=tk.WORD, bg="#ecf0f1", fg="#2c3e50", 
                                 relief=tk.FLAT, bd=5, state=tk.DISABLED)
        
        input_scrollbar = ttk.Scrollbar(input_scroll_frame, orient=tk.VERTICAL, command=self.input_text.yview)
        self.input_text.configure(yscrollcommand=input_scrollbar.set)
        
        self.input_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        input_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.input_text.bind('<KeyPress>', self.on_key_press)
        self.input_text.bind('<Key>', self.on_key_event)
        
        # Control buttons
        button_frame = tk.Frame(self.root, bg="#2c3e50")
        button_frame.pack(pady=20)
        
        self.start_button = tk.Button(button_frame, text="Start Test", font=("Arial", 14, "bold"), 
                                     bg="#27ae60", fg="white", padx=20, pady=10, 
                                     command=self.start_test)
        self.start_button.pack(side=tk.LEFT, padx=10)
        
        self.new_text_button = tk.Button(button_frame, text="New Text", font=("Arial", 14, "bold"), 
                                        bg="#3498db", fg="white", padx=20, pady=10, 
                                        command=self.select_new_text)
        self.new_text_button.pack(side=tk.LEFT, padx=10)
        
        self.reset_button = tk.Button(button_frame, text="Reset", font=("Arial", 14, "bold"), 
                                     bg="#e74c3c", fg="white", padx=20, pady=10, 
                                     command=self.reset_test)
        self.reset_button.pack(side=tk.LEFT, padx=10)
        
        self.history_button = tk.Button(button_frame, text="View History", font=("Arial", 14, "bold"), 
                                       bg="#9b59b6", fg="white", padx=20, pady=10, 
                                       command=self.show_history)
        self.history_button.pack(side=tk.LEFT, padx=10)
        
        self.export_button = tk.Button(button_frame, text="Export Results", font=("Arial", 14, "bold"), 
                                      bg="#f39c12", fg="white", padx=20, pady=10, 
                                      command=self.export_results)
        self.export_button.pack(side=tk.LEFT, padx=10)
        
    def change_mode(self, event=None):
        mode = self.mode_var.get()
        if mode == "Complete Text":
            self.test_duration = None
            self.time_label.config(text="Time: Complete Text")
        else:
            self.test_duration = int(mode.split()[0])
            self.remaining_time = self.test_duration
            self.time_label.config(text=f"Time: {self.remaining_time}s")
        
    def select_new_text(self):
        """Select a random text that's different from the current one"""
        if len(self.test_texts) > 1:
            available_texts = [i for i in range(len(self.test_texts)) if i != getattr(self, 'current_text_index', -1)]
            self.current_text_index = random.choice(available_texts)
        else:
            self.current_text_index = 0
            
        self.current_text = self.test_texts[self.current_text_index]
        
        # Update text info
        categories = ["Technology", "Technology", "Technology", "Technology", "Technology",
                     "Science", "Science", "Science", "Science", "Science",
                     "History", "History", "History", "History", "History",
                     "Literature", "Literature", "Literature", "Literature", "Literature",
                     "Business", "Business", "Business", "Business", "Business",
                     "Health", "Health", "Health", "Travel", "Travel",
                     "Environment", "Environment", "Environment"]
        
        category = categories[self.current_text_index] if self.current_text_index < len(categories) else "General"
        self.text_info_label.config(text=f"Text {self.current_text_index + 1}/{len(self.test_texts)} ({category})")
        
        self.display_text()
        self.reset_test()
        
    def display_text(self):
        self.text_display.config(state=tk.NORMAL)
        self.text_display.delete("1.0", tk.END)
        self.text_display.insert(tk.END, self.current_text)
        self.text_display.config(state=tk.DISABLED)
        
    def start_test(self):
        if not self.test_active:
            self.test_active = True
            self.start_time = time.time()
            if self.test_duration:
                self.remaining_time = self.test_duration
                self.start_timer()
            self.input_text.config(state=tk.NORMAL)
            self.input_text.focus()
            self.start_button.config(text="Test Running...", state=tk.DISABLED, bg="#95a5a6")
        
    def start_timer(self):
        def countdown():
            while self.remaining_time > 0 and self.test_active:
                self.time_label.config(text=f"Time: {self.remaining_time}s")
                time.sleep(1)
                self.remaining_time -= 1
                
            if self.test_active and self.test_duration:
                self.end_test()
                
        if self.test_duration:
            timer_thread = threading.Thread(target=countdown)
            timer_thread.daemon = True
            timer_thread.start()
        
    def on_key_press(self, event):
        if not self.test_active:
            return "break"
            
    def on_key_event(self, event):
        if not self.test_active:
            return
            
        # Update statistics in real-time
        self.root.after(10, self.update_stats)
        
    def update_stats(self):
        if not self.test_active:
            return
            
        typed_content = self.input_text.get("1.0", tk.END).rstrip()
        self.total_chars = len(typed_content)
        
        # Check if test is complete (for complete text mode)
        if not self.test_duration and self.total_chars >= len(self.current_text):
            # Check if the text matches exactly
            if typed_content == self.current_text:
                self.end_test()
                return
            elif self.total_chars > len(self.current_text):
                # Prevent typing beyond the text
                self.input_text.delete(f"1.{len(self.current_text)}", tk.END)
                typed_content = self.input_text.get("1.0", tk.END).rstrip()
                self.total_chars = len(typed_content)
        
        # Calculate correct characters and errors
        self.correct_chars = 0
        self.errors = 0
        
        for i, char in enumerate(typed_content):
            if i < len(self.current_text):
                if char == self.current_text[i]:
                    self.correct_chars += 1
                else:
                    self.errors += 1
            else:
                self.errors += 1
                
        # Calculate WPM and accuracy
        if self.start_time:
            elapsed_time = time.time() - self.start_time
            if elapsed_time > 0:
                # WPM calculation: (total characters / 5) / (time in minutes)
                wpm = (self.total_chars / 5) / (elapsed_time / 60)
                self.wpm_label.config(text=f"WPM: {wpm:.1f}")
                
                # Update time for complete text mode
                if not self.test_duration:
                    self.time_label.config(text=f"Time: {elapsed_time:.1f}s")
                
        # Accuracy calculation
        if self.total_chars > 0:
            accuracy = (self.correct_chars / self.total_chars) * 100
            self.accuracy_label.config(text=f"Accuracy: {accuracy:.1f}%")
        else:
            self.accuracy_label.config(text="Accuracy: 100%")
            
        # Progress calculation
        progress = min((self.total_chars / len(self.current_text)) * 100, 100)
        self.progress_label.config(text=f"Progress: {progress:.1f}%")
            
        self.errors_label.config(text=f"Errors: {self.errors}")
        
        # Highlight text
        self.highlight_text(typed_content)
        
    def highlight_text(self, typed_content):
        self.text_display.config(state=tk.NORMAL)
        self.text_display.delete("1.0", tk.END)
        
        # Configure tags for highlighting
        self.text_display.tag_configure("correct", background="#d5f4e6", foreground="#27ae60")
        self.text_display.tag_configure("incorrect", background="#fadbd8", foreground="#e74c3c")
        self.text_display.tag_configure("current", background="#fff3cd", foreground="#856404")
        self.text_display.tag_configure("untyped", background="#ecf0f1", foreground="#7f8c8d")
        
        for i, char in enumerate(self.current_text):
            if i < len(typed_content):
                if typed_content[i] == char:
                    self.text_display.insert(tk.END, char, "correct")
                else:
                    self.text_display.insert(tk.END, char, "incorrect")
            elif i == len(typed_content):
                self.text_display.insert(tk.END, char, "current")
            else:
                self.text_display.insert(tk.END, char, "untyped")
                
        self.text_display.config(state=tk.DISABLED)
        
    def end_test(self):
        self.test_active = False
        self.input_text.config(state=tk.DISABLED)
        self.start_button.config(text="Start Test", state=tk.NORMAL, bg="#27ae60")
        
        # Final calculations
        if self.start_time:
            elapsed_time = time.time() - self.start_time
            if self.test_duration:
                test_time = self.test_duration
            else:
                test_time = elapsed_time
                
            wpm = (self.total_chars / 5) / (elapsed_time / 60)
            accuracy = (self.correct_chars / self.total_chars * 100) if self.total_chars > 0 else 100
            net_wpm = wpm * (accuracy / 100)
            
            # Save results
            result = {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "text_number": self.current_text_index + 1,
                "test_mode": self.mode_var.get(),
                "elapsed_time": round(elapsed_time, 1),
                "wpm": round(wpm, 1),
                "net_wpm": round(net_wpm, 1),
                "accuracy": round(accuracy, 1),
                "errors": self.errors,
                "total_chars": self.total_chars,
                "text_length": len(self.current_text),
                "completion": round((self.total_chars / len(self.current_text)) * 100, 1)
            }
            
            self.test_history.append(result)
            self.save_history()
            
            # Show results
            self.show_results(result)
        
    def show_results(self, result):
        result_window = tk.Toplevel(self.root)
        result_window.title("Test Results")
        result_window.geometry("450x400")
        result_window.configure(bg="#2c3e50")
        result_window.transient(self.root)
        result_window.grab_set()
        
        # Center the window
        result_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        tk.Label(result_window, text="🎉 Test Complete! 🎉", font=("Arial", 18, "bold"), 
                fg="#ecf0f1", bg="#2c3e50").pack(pady=20)
        
        stats_frame = tk.Frame(result_window, bg="#34495e", relief=tk.RAISED, bd=2)
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        stats = [
            ("Test Mode:", result['test_mode']),
            ("Text Number:", f"{result['text_number']}/{len(self.test_texts)}"),
            ("Completion:", f"{result['completion']:.1f}%"),
            ("Time Taken:", f"{result['elapsed_time']:.1f}s"),
            ("Gross WPM:", f"{result['wpm']:.1f}"),
            ("Net WPM:", f"{result['net_wpm']:.1f}"),
            ("Accuracy:", f"{result['accuracy']:.1f}%"),
            ("Errors:", str(result['errors'])),
            ("Characters Typed:", f"{result['total_chars']}/{result['text_length']}")
        ]
        
        for label, value in stats:
            frame = tk.Frame(stats_frame, bg="#34495e")
            frame.pack(fill=tk.X, padx=10, pady=3)
            tk.Label(frame, text=label, font=("Arial", 11, "bold"), 
                    fg="#ecf0f1", bg="#34495e").pack(side=tk.LEFT)
            tk.Label(frame, text=value, font=("Arial", 11), 
                    fg="#3498db", bg="#34495e").pack(side=tk.RIGHT)
        
        # Performance feedback
        feedback = self.get_performance_feedback(result['wpm'], result['accuracy'], result['completion'])
        tk.Label(result_window, text=feedback, font=("Arial", 11), 
                fg="#f1c40f", bg="#2c3e50", wraplength=400).pack(pady=10)
        
        button_frame = tk.Frame(result_window, bg="#2c3e50")
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="New Text", command=lambda: [result_window.destroy(), self.select_new_text()], 
                 font=("Arial", 12), bg="#3498db", fg="white", padx=15).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Same Text", command=lambda: [result_window.destroy(), self.reset_test()], 
                 font=("Arial", 12), bg="#27ae60", fg="white", padx=15).pack(side=tk.LEFT, padx=5)
        tk.Button(result_window, text="Close", command=result_window.destroy, 
                 font=("Arial", 12), bg="#e74c3c", fg="white", padx=20).pack(pady=5)
        
    def get_performance_feedback(self, wpm, accuracy, completion):
        if completion < 50:
            return "💪 Keep practicing! Try to complete more of the text for better results."
        elif completion >= 100 and wpm >= 80 and accuracy >= 95:
            return "🔥 Excellent! You're a typing master with perfect completion!"
        elif completion >= 100 and wpm >= 60 and accuracy >= 90:
            return "⭐ Great job! Perfect completion with very good typing skills!"
        elif completion >= 100 and wpm >= 40 and accuracy >= 85:
            return "👍 Good work! You completed the text - keep practicing to improve speed!"
        elif wpm >= 60 and accuracy >= 90:
            return "🚀 Great speed and accuracy! Try to complete more text next time."
        elif wpm >= 40 and accuracy >= 85:
            return "📈 Good progress! Focus on both speed and completion."
        else:
            return "📚 Keep practicing! Remember: accuracy and completion are more important than speed!"
        
    def reset_test(self):
        self.test_active = False
        self.start_time = None
        if self.test_duration:
            self.remaining_time = self.test_duration
            self.time_label.config(text=f"Time: {self.remaining_time}s")
        else:
            self.time_label.config(text="Time: --")
        self.typed_text = ""
        self.correct_chars = 0
        self.total_chars = 0
        self.errors = 0
        
        # Reset UI
        self.input_text.config(state=tk.NORMAL)
        self.input_text.delete("1.0", tk.END)
        self.input_text.config(state=tk.DISABLED)
        self.start_button.config(text="Start Test", state=tk.NORMAL, bg="#27ae60")
        
        # Reset statistics display
        self.wpm_label.config(text="WPM: 0")
        self.accuracy_label.config(text="Accuracy: 100%")
        self.progress_label.config(text="Progress: 0%")
        self.errors_label.config(text="Errors: 0")
        
        # Reset text display
        self.display_text()
        
    def show_history(self):
        if not self.test_history:
            messagebox.showinfo("History", "No test history available yet!")
            return
            
        history_window = tk.Toplevel(self.root)
        history_window.title("Test History")
        history_window.geometry("1000x600")
        history_window.configure(bg="#2c3e50")
        
        tk.Label(history_window, text="📊 Test History", font=("Arial", 18, "bold"), 
                fg="#ecf0f1", bg="#2c3e50").pack(pady=10)
        
        # Create treeview for history
        frame = tk.Frame(history_window, bg="#2c3e50")
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        columns = ("Date", "Text", "Mode", "Time", "WPM", "Net WPM", "Accuracy", "Completion", "Errors")
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            if col in ["Date"]:
                tree.column(col, width=150)
            elif col in ["Mode"]:
                tree.column(col, width=120)
            else:
                tree.column(col, width=80)
            
        # Add scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate history
        for result in reversed(self.test_history):  # Most recent first
            tree.insert("", tk.END, values=(
                result["date"],
                f"{result['text_number']}/{len(self.test_texts)}",
                result["test_mode"],
                f"{result['elapsed_time']:.1f}s",
                f"{result['wpm']:.1f}",
                f"{result['net_wpm']:.1f}",
                f"{result['accuracy']:.1f}%",
                f"{result['completion']:.1f}%",
                result['errors']
            ))
            
        # Statistics
        if self.test_history:
            avg_wpm = sum(r['wpm'] for r in self.test_history) / len(self.test_history)
            avg_accuracy = sum(r['accuracy'] for r in self.test_history) / len(self.test_history)
            avg_completion = sum(r['completion'] for r in self.test_history) / len(self.test_history)
            best_wpm = max(r['wpm'] for r in self.test_history)
            
            stats_text = f"Tests taken: {len(self.test_history)} | Avg WPM: {avg_wpm:.1f} | Avg Accuracy: {avg_accuracy:.1f}% | Avg Completion: {avg_completion:.1f}% | Best WPM: {best_wpm:.1f}"
            tk.Label(history_window, text=stats_text, font=("Arial", 11), 
                    fg="#3498db", bg="#2c3e50", wraplength=950).pack(pady=10)
        
    def export_results(self):
        if not self.test_history:
            messagebox.showinfo("Export", "No test history to export!")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export Test Results"
        )
        
        if filename:
            try:
                if filename.endswith('.json'):
                    with open(filename, 'w') as f:
                        json.dump(self.test_history, f, indent=2)
                elif filename.endswith('.csv'):
                    with open(filename, 'w') as f:
                        f.write("Date,Text_Number,Test_Mode,Elapsed_Time,WPM,Net_WPM,Accuracy,Errors,Total_Chars,Text_Length,Completion\n")
                        for result in self.test_history:
                            f.write(f"{result['date']},{result['text_number']},{result['test_mode']},{result['elapsed_time']:.1f},{result['wpm']:.1f},{result['net_wpm']:.1f},{result['accuracy']:.1f},{result['errors']},{result['total_chars']},{result['text_length']},{result['completion']:.1f}\n")
                            
                messagebox.showinfo("Export", f"Results exported successfully to {filename}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export results: {str(e)}")
        
    def load_history(self):
        try:
            if os.path.exists("advanced_typing_history.json"):
                with open("advanced_typing_history.json", "r") as f:
                    self.test_history = json.load(f)
        except Exception as e:
            print(f"Error loading history: {e}")
            self.test_history = []
            
    def save_history(self):
        try:
            with open("advanced_typing_history.json", "w") as f:
                json.dump(self.test_history, f, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedTypingSpeedTest(root)
    root.mainloop()
