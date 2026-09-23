"""
Sample documents for demonstration.
Contains:
  1. Original academic paragraph
  2. Heavy paraphrase of the same content (should be flagged)
  3. Completely different text (should score low)
"""

ORIGINAL = """
Artificial intelligence has transformed numerous industries by enabling machines to perform tasks that traditionally required human intelligence. Machine learning algorithms can analyse large datasets to identify patterns and make predictions with remarkable accuracy. In healthcare, AI systems assist doctors in diagnosing diseases from medical images and predicting patient outcomes. Natural language processing allows computers to understand and generate human language, powering applications such as chatbots and translation services. Despite these advances, concerns remain about data privacy, algorithmic bias, and the potential displacement of human workers. Researchers continue to develop more transparent and ethical AI systems that can be trusted in critical decision-making scenarios.
"""

PARAPHRASED = """
The field of artificial intelligence has revolutionised many sectors by allowing computers to execute activities that once depended on human cognition. Algorithms based on machine learning are capable of examining vast collections of data in order to discover trends and generate forecasts with high precision. Within the medical domain, intelligent systems help physicians detect illnesses using scans and estimate how patients will progress. Through natural language processing, machines can interpret and produce spoken or written language, which supports tools like virtual assistants and automated translators. Nevertheless, issues related to the confidentiality of information, unfair bias in models, and the risk that automation may replace human jobs still exist. Scientists are persistently creating AI solutions that are more interpretable and morally sound so they can be relied upon for important choices.
"""

DIFFERENT = """
Climate change represents one of the most pressing challenges of the twenty-first century. Rising global temperatures are causing polar ice caps to melt, leading to higher sea levels and more frequent extreme weather events. Governments and international organisations have set ambitious targets to reduce greenhouse gas emissions through renewable energy adoption and carbon pricing mechanisms. Individual actions such as reducing meat consumption, using public transport, and improving home energy efficiency also contribute to mitigation efforts. Scientific consensus indicates that immediate and coordinated action is essential to limit warming to 1.5 degrees Celsius above pre-industrial levels.
"""

# Slightly modified version that keeps some structure (should still be detected)
LIGHTLY_EDITED = """
Artificial intelligence has changed many industries by enabling machines to perform tasks that traditionally required human intelligence. Machine learning algorithms can examine large datasets to find patterns and make predictions with high accuracy. In the healthcare sector, AI systems help doctors diagnose diseases from medical images and predict patient outcomes. Natural language processing enables computers to understand and generate human language, powering apps such as chatbots and translation tools. Despite these advances, worries remain about data privacy, algorithmic bias, and possible job losses for human workers. Researchers keep developing more transparent and ethical AI systems that can be trusted for critical decisions.
"""
