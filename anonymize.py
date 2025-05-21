from presidio_analyzer import AnalyzerEngine, PatternRecognizer
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import RecognizerResult
from presidio_anonymizer.entities  import OperatorConfig

# Define the NLP configuration
configuration = {
    "nlp_engine_name": "spacy",
    "models": [{"lang_code": "en", "model_name": "en_core_web_trf"}],
}


# Create the NLP engine
provider = NlpEngineProvider(nlp_configuration=configuration)
nlp_engine = provider.create_engine()


# Load your transformer model
def load_trf_model():
    spacy.cli.download("en_core_web_trf")  # installs only if missing
    return spacy.load("en_core_web_trf")

nlp = load_trf_model()


def analyzer_results(text: str) -> str:
    
    """
    Use Presidio to detect PII entities with generic placeholders.
    Returns analyzed text.
    """
    # Initialize the Presidio analyzer engine
    analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["en"])
    
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

# print(anonymize("My name Rani"))
print(anonymizer(text_to_anonymize))

