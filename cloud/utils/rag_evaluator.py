from typing import Iterable, Sequence, Any
from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd
from unitxt.eval_utils import evaluate


@dataclass
class EvaluationData:
    """
    Representation of data sent for evaluation.

    Parameters
    ----------
    question : str | None, default=None
        Original question from the benchmark dataset

    answer : str | None, default=None
        Answer returned by the model.

    contexts : list[str] | None = None
        Contexts used by the model to generate response.

    context_ids: list[str] | None, default=None
        IDs of contexts used by the model to generate response.

    ground_truths : list[str] | None = None
        Correct answers from the benchmark dataset.

    ground_truths_context_ids : list[str] | None = None
        IDs of the correct documents used for answers in the benchmark dataset.

    question_id : str | None = None
        ID of the question.

    additional_data: dict[str, Any] | None = None
        Any additional data associated with the evaluation results.

    Methods
    -------
    to_dict() -> dict[str, Any]
        Used for casting instance to the dictionary
    """

    question: str | None = None
    answer: str | None = None
    contexts: list[str] | None = None
    context_ids: list[str] | None = None
    ground_truths: list[str] | None = None
    ground_truths_context_ids: list[str] | None = None
    question_id: str | None = None
    additional_data: list[Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Cast given instance of dataclass to the dict."""
        return asdict(self)


class MetricType:
    """
    Holder for metric names.

    Attributes
    ----------
    ANSWER_CORRECTNESS : str, default="answer_correctness"

    CONTEXT_RELEVANCY : str, default="context_relevancy"

    FAITHFULNESS : str, default="faithfulness"

    ANSWER_REWARD : str, default="answer_reward"

    CONTEXT_CORRECTNESS : str, default="context_correctness"

    CONTEXT_CORRECTNESS_MAP : str, default="context_correctness_map"

    CONTEXT_PERPLEXITY : str, default="context_perplexity"
    """

    ANSWER_CORRECTNESS = "answer_correctness"
    CONTEXT_RELEVANCY = "context_relevancy"
    FAITHFULNESS = "faithfulness"
    ANSWER_REWARD = "answer_reward"
    CONTEXT_CORRECTNESS = "context_correctness"
    CONTEXT_CORRECTNESS_MAP = "context_correctness_map"
    CONTEXT_PERPLEXITY = "context_perplexity"


class EvaluationException(Exception):
    """
    Raised for evaluation errors of mis-configurations.
    """

    pass


class UnitxtEvaluator:
    """Unitxt wrapper making evaluation of the RAG's usage."""

    METRIC_TYPE_MAP = {
        MetricType.ANSWER_CORRECTNESS: "metrics.rag.answer_correctness",
        MetricType.CONTEXT_RELEVANCY: "metrics.rag.context_relevance",
        MetricType.FAITHFULNESS: "metrics.rag.faithfulness",
        MetricType.ANSWER_REWARD: "metrics.rag.answer_reward",
        MetricType.CONTEXT_CORRECTNESS: "metrics.rag.context_correctness",
        MetricType.CONTEXT_CORRECTNESS_MAP: "metrics.rag.map",
        MetricType.CONTEXT_PERPLEXITY: "metrics.rag.context_perplexity",
    }

    def evaluate_metrics(
        self,
        evaluation_data: Iterable[EvaluationData],
        metrics: Sequence[str],
    ) -> dict:
        """
        Perform evaluation on the given instances with chosen metric types.

        Parameters
        ----------
        evaluation_data : Iterable[EvaluationData]
            Iterable of instances that hold data needed for the unitxt
            algorithms to perform evaluation.

        metrics : Sequence[str]
            Values describing which specific evaluation metrics should be used
            withing evaluation process.

        Returns
        -------
        dict
            Dictionary of scores given for each EvaluationData.
        """
        evaluation_primitives = [prim.to_dict() for prim in evaluation_data]
        df = pd.DataFrame(evaluation_primitives)
        unitxt_metrics = self.get_metric_types(metric_types=metrics)
        try:
            res_df, ci_table = evaluate(df, metric_names=unitxt_metrics, compute_conf_intervals=True)
            res_df.replace("", np.nan, inplace=True)
            ci_table.replace(np.nan, None, inplace=True)

            raw_ret_dict = res_df.round(4).to_dict()
            ci_dict = ci_table.to_dict()

            reversed_metrics_mapping = {v: k for k, v in self.METRIC_TYPE_MAP.items()}
            without_id = {
                reversed_metrics_mapping[key]: val
                for key, val in raw_ret_dict.items()
                if key in reversed_metrics_mapping
            }

            question_scores = {}
            for key, val in without_id.items():
                question_scores[key] = {raw_ret_dict["question_id"][k]: v for k, v in val.items()}

            def round_or_none(x: float | None) -> float | None:
                return None if x is None else round(x, 4)

            fixed_ci = {}
            for key, val in ci_dict.items():
                score_name = self._get_score_name(key)
                fixed_ci[reversed_metrics_mapping[key]] = {
                    "mean": round_or_none(val["score"]),
                    "ci_low": round_or_none(val.get(f"{score_name}_ci_low")),
                    "ci_high": round_or_none(val.get(f"{score_name}_ci_high")),
                }

            ret = {"scores": fixed_ci, "question_scores": question_scores}

            return ret
        except Exception as err:
            raise EvaluationException(err)

    @classmethod
    def get_metric_types(cls, metric_types: Sequence[str]) -> list[str]:
        """
        Perform mapping of general metric names to the specific metric names
        in the unitxt library.

        Parameters
        ----------
        metric_types : Sequence[str]
            Metrics defined in the MetricType class.

        Returns
        -------
        list
            Specific versions of the metrics that can be used within
            unitxt evaluation process.
        """
        mapping = [cls.METRIC_TYPE_MAP.get(metric, None) for metric in metric_types]
        return [metric for metric in mapping if metric is not None]

    @classmethod
    def decode_unitxt_metric(cls, unitxt_metrics: list[str]) -> list[str]:
        """
        Decode metrics from the unitxt names to general names.

        Parameters
        ----------
        unitxt_metrics : list[str]
            Encoded unitxt metrics.

        Returns
        -------
        list[str]
            Corresponding decoded messages
        """

        reversed_mapping = {v: k for k, v in cls.METRIC_TYPE_MAP.items()}
        decoded = [reversed_mapping[metric] for metric in unitxt_metrics]

        return decoded

    @classmethod
    def _get_score_name(cls, metric: str) -> str:
        """
        In unitxt we do not have consistency across score names used for
        confidence intervals. This is a temporary fix until it is provided
        in unitxt.

        Parameters
        ----------
        metric : str
            Metric understandable by unitxt

        Returns
        -------
        Proper score name for metric value calculation
        """
        score_names_mapping = {
            cls.METRIC_TYPE_MAP[MetricType.FAITHFULNESS]: "precision",  # Incorrectly unitxt suggests f1
            cls.METRIC_TYPE_MAP[MetricType.ANSWER_CORRECTNESS]: "recall",  # Incorrectly unitxt suggests f1
            cls.METRIC_TYPE_MAP[MetricType.CONTEXT_CORRECTNESS]: "mrr",
            cls.METRIC_TYPE_MAP[MetricType.CONTEXT_CORRECTNESS_MAP]: "map",
        }

        return score_names_mapping.get(metric)
