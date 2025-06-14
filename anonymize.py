from presidio_analyzer import AnalyzerEngine, PatternRecognizer, EntityRecognizer
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import RecognizerResult
from presidio_anonymizer.entities  import OperatorConfig


def analyzer_results(text: str) -> str:
    
    """
    Use Presidio to detect PII entities with generic placeholders.
    Returns analyzed text.
    """
    # Initialize the Presidio analyzer engine
    analyzer = AnalyzerEngine()
    

    # Run the anonymizer, returns list of recognizer results
    analyzer_results = analyzer.analyze(text=text,  language='en')

    return analyzer_results

def anonymizer(text: str) -> str:
    """
    Use Presidio to detect and replace PII entities with generic placeholders.
    Returns anonymized text.
    """
    # Initialize the Presidio anonymizer engine
    anonymizer = AnonymizerEngine()
    

    # Run the anonymizer, returns list of recognizer results
    
    anonymized_results = anonymizer.anonymize(
        text=text,
        analyzer_results=analyzer_results(text), 
    )
    return anonymized_results.text





text_to_anonymize = "His name is Mr. Jones and his phone number is 212-555-5555"

print(anonymizer(text_to_anonymize))

