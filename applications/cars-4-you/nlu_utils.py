from watson_developer_cloud import NaturalLanguageUnderstandingV1
from watson_developer_cloud.natural_language_understanding_v1 import \
    Features, EntitiesOptions, KeywordsOptions, CategoriesOptions


class NLUUtils:
    """NLUUtils class defines connection to NLU service and provides a way to analyze text sentiment."""
    def __init__(self, nlu_vcap: dict) -> None:
        self.version = nlu_vcap["version"]
        self.url = nlu_vcap["url"]
        self.apikey = nlu_vcap["apikey"]

        self.nlu = NaturalLanguageUnderstandingV1(
            version=self.version, url=self.url, iam_apikey=self.apikey)

        self.features = Features(categories=CategoriesOptions(), entities=EntitiesOptions(
            emotion=True, sentiment=True), keywords=KeywordsOptions(emotion=True, sentiment=True))

    def analyze_sentiment(self, text: str) -> str:
        """Analyze text sentiment

        Parameters
        ----------
        text: str, required
            Text for analysis

        Returns
        -------
        String with sentiment.
        """
        try:
            response = self.nlu.analyze(text=text, features=self.features)

            neg_count = 0
            pos_count = 0
            neut_count = 0

            for kw in response['keywords']:
                if kw['sentiment']['label'] == 'positive':
                    pos_count += 1
                elif kw['sentiment']['label'] == 'negative':
                    neg_count += 1
                else:
                    neut_count += 1

            if pos_count > neg_count and pos_count > neut_count:
                return 'positive'
            elif neg_count > pos_count and neg_count > neut_count:
                return 'negative'
            elif neut_count > pos_count and neut_count > neg_count:
                return 'neutral'
            elif neut_count == pos_count and neut_count > neg_count:
                return 'neutral'
            elif neg_count == pos_count and neg_count > neut_count:
                return 'neutral'
            elif neut_count == neg_count and neut_count > pos_count:
                return 'neutral'
            elif neut_count == pos_count and neut_count == neg_count:
                return 'neutral'
        except Exception:
            return 'neutral'
