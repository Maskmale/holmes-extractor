import unittest
import holmes_extractor as holmes
from holmes_extractor.errors import *
import jsonpickle

nocoref_holmes_manager = holmes.Manager('en_core_web_trf', analyze_derivational_morphology=False,
                                        perform_coreference_resolution=False, number_of_workers=2)
coref_holmes_manager = holmes.Manager(
    'en_core_web_trf', perform_coreference_resolution=True, number_of_workers=1)
german_holmes_manager = holmes.Manager('de_core_news_lg', number_of_workers=1)


class ErrorsTest(unittest.TestCase):

    def test_overall_similarity_threshold_out_of_range(self):
        with self.assertRaises(ValueError) as context:
            holmes.Manager(model='en_core_web_lg',
                           overall_similarity_threshold=1.2)

    def test_embedding_based_matching_on_root_node_where_no_embedding_based_matching(self):
        with self.assertRaises(ValueError) as context:
            holmes.Manager(model='en_core_web_lg', overall_similarity_threshold=1.0,
                           embedding_based_matching_on_root_words=True)

    def test_number_of_workers_out_of_range(self):
        with self.assertRaises(ValueError) as context:
            holmes.Manager(model='en_core_web_sm',
                           number_of_workers=0)

    def test_language_not_supported(self):
        with self.assertRaises(ValueError) as context:
            holmes.Manager(model='pl_core_news_md')

    def test_search_phrase_contains_conjunction(self):
        with self.assertRaises(SearchPhraseContainsConjunctionError) as context:
            nocoref_holmes_manager.remove_all_search_phrases()
            nocoref_holmes_manager.register_search_phrase(
                "A dog and a lion chase a cat")

    def test_search_phrase_contains_negation(self):
        with self.assertRaises(SearchPhraseContainsNegationError) as context:
            nocoref_holmes_manager.remove_all_search_phrases()
            nocoref_holmes_manager.register_search_phrase(
                "A dog does not chase a cat")

    def test_search_phrase_contains_pronoun_coreference_switched_off(self):
        nocoref_holmes_manager.remove_all_search_phrases()
        nocoref_holmes_manager.register_search_phrase(
            "A dog has a cat chasing it")

    def test_search_phrase_contains_coreferring_pronoun(self):
        with self.assertRaises(SearchPhraseContainsCoreferringPronounError) as context:
            coref_holmes_manager.remove_all_search_phrases()
            coref_holmes_manager.register_search_phrase(
                "A dog has a cat chasing it")

    def test_search_phrase_contains_only_generic_pronoun(self):
        with self.assertRaises(SearchPhraseWithoutMatchableWordsError) as context:
            nocoref_holmes_manager.remove_all_search_phrases()
            nocoref_holmes_manager.register_search_phrase("Somebody")

    def test_search_phrase_contains_only_interrogative_pronoun(self):
        with self.assertRaises(SearchPhraseWithoutMatchableWordsError) as context:
            nocoref_holmes_manager.remove_all_search_phrases()
            nocoref_holmes_manager.register_search_phrase("Who")

    def test_search_phrase_contains_only_grammatical_word(self):
        with self.assertRaises(SearchPhraseWithoutMatchableWordsError) as context:
            nocoref_holmes_manager.remove_all_search_phrases()
            nocoref_holmes_manager.register_search_phrase("the")

    def test_search_phrase_contains_two_normal_clauses(self):
        with self.assertRaises(SearchPhraseContainsMultipleClausesError) as context:
            nocoref_holmes_manager.remove_all_search_phrases()
            nocoref_holmes_manager.register_search_phrase(
                "The dog chased the cat. The cat chased the dog.")

    def test_search_phrase_contains_two_entity_clauses(self):
        with self.assertRaises(SearchPhraseContainsMultipleClausesError) as context:
            nocoref_holmes_manager.remove_all_search_phrases()
            nocoref_holmes_manager.register_search_phrase(
                "An ENTITYPERSON. An ENTITYPERSON")

    def test_search_phrase_contains_one_normal_and_one_entity_clause(self):
        with self.assertRaises(SearchPhraseContainsMultipleClausesError) as context:
            nocoref_holmes_manager.remove_all_search_phrases()
            nocoref_holmes_manager.register_search_phrase(
                "The dog chased the cat. An ENTITYPERSON")

    def test_duplicate_document_with_parse_and_register_document(self):
        with self.assertRaises(DuplicateDocumentError) as context:
            nocoref_holmes_manager.remove_all_documents()
            nocoref_holmes_manager.parse_and_register_document("A", "A")
            nocoref_holmes_manager.parse_and_register_document("A", "A")

    def test_duplicate_document_with_register_serialized_document(self):
        with self.assertRaises(DuplicateDocumentError) as context:
            nocoref_holmes_manager.remove_all_documents()
            nocoref_holmes_manager.parse_and_register_document("A", '')
            deserialized_doc = nocoref_holmes_manager.serialize_document('')
            nocoref_holmes_manager.register_serialized_document(
                deserialized_doc, '')

    def test_duplicate_document_with_register_serialized_documents(self):
        with self.assertRaises(DuplicateDocumentError) as context:
            nocoref_holmes_manager.remove_all_documents()
            nocoref_holmes_manager.parse_and_register_document("A", '')
            deserialized_doc = nocoref_holmes_manager.serialize_document('')
            nocoref_holmes_manager.register_serialized_documents(
                {'': deserialized_doc})

    def test_no_search_phrase_error(self):
        with self.assertRaises(NoSearchPhraseError) as context:
            nocoref_holmes_manager.remove_all_search_phrases()
            nocoref_holmes_manager.match(document_text="Try this")

    def test_no_document_error_structural_match(self):
        with self.assertRaises(NoDocumentError) as context:
            nocoref_holmes_manager.remove_all_documents()
            nocoref_holmes_manager.match(search_phrase_text="Try this")

    def test_no_document_error_topic_match(self):
        with self.assertRaises(NoDocumentError) as context:
            nocoref_holmes_manager.remove_all_documents()
            nocoref_holmes_manager.topic_match_documents_against(text_to_match="Try this")

    def test_wrong_model_deserialization_error_documents(self):
        with self.assertRaises(WrongModelDeserializationError) as context:
            nocoref_holmes_manager.remove_all_documents()
            doc = nocoref_holmes_manager.parse_and_register_document(
                "The cat was chased by the dog", 'pets')
            serialized_doc = nocoref_holmes_manager.serialize_document('pets')
            german_holmes_manager.register_serialized_document(
                serialized_doc, 'pets')

    def test_wrong_version_deserialization_error_documents(self):
        with self.assertRaises(WrongVersionDeserializationError) as context:
            nocoref_holmes_manager.remove_all_documents()
            nocoref_holmes_manager.parse_and_register_document(
                "The cat was chased by the dog", 'pets')
            doc = nocoref_holmes_manager.get_document('pets')
            doc._.holmes_document_info.serialized_document_version = 1
            nocoref_holmes_manager.register_serialized_document(
                doc.to_bytes(), 'pets2')

    def test_wrong_model_deserialization_error_supervised_models(self):
        with self.assertRaises(WrongModelDeserializationError) as context:
            sttb = german_holmes_manager.get_supervised_topic_training_basis()
            sttb.parse_and_register_training_document("Katze", 'Tiere', 't1')
            sttb.parse_and_register_training_document("Katze", 'IT', 't2')
            sttb.prepare()
            stc = sttb.train(minimum_occurrences=0,
                             cv_threshold=0).classifier()
            serialized_supervised_topic_classifier_model = stc.serialize_model()
            stc2 = coref_holmes_manager.deserialize_supervised_topic_classifier(
                serialized_supervised_topic_classifier_model)

    def test_derivational_morphology_deserialization_error_supervised_models_true_false(self):
        with self.assertRaises(IncompatibleAnalyzeDerivationalMorphologyDeserializationError) \
                as context:
            sttb = nocoref_holmes_manager.get_supervised_topic_training_basis()
            sttb.parse_and_register_training_document("cat", 'animal', 't1')
            sttb.parse_and_register_training_document("mouse", 'IT', 't2')
            sttb.prepare()
            stc = sttb.train(minimum_occurrences=0,
                             cv_threshold=0).classifier()
            serialized_supervised_topic_classifier_model = stc.serialize_model()
            stc2 = coref_holmes_manager.deserialize_supervised_topic_classifier(
                serialized_supervised_topic_classifier_model)

    def test_derivational_morphology_deserialization_error_supervised_models_false_true(self):
        with self.assertRaises(IncompatibleAnalyzeDerivationalMorphologyDeserializationError) \
                as context:
            sttb = coref_holmes_manager.get_supervised_topic_training_basis()
            sttb.parse_and_register_training_document("cat", 'animal', 't1')
            sttb.parse_and_register_training_document("mouse", 'IT', 't2')
            sttb.prepare()
            stc = sttb.train(minimum_occurrences=0,
                             cv_threshold=0).classifier()
            serialized_supervised_topic_classifier_model = stc.serialize_model()
            stc2 = nocoref_holmes_manager.deserialize_supervised_topic_classifier(
                serialized_supervised_topic_classifier_model)

    def test_fewer_than_two_classifications_error(self):
        with self.assertRaises(FewerThanTwoClassificationsError) as context:
            sttb = german_holmes_manager.get_supervised_topic_training_basis()
            sttb.parse_and_register_training_document("Katze", 'Tiere', 't1')
            sttb.prepare()

    def test_duplicate_document_with_train_supervised_model(self):
        with self.assertRaises(DuplicateDocumentError) as context:
            sttb = german_holmes_manager.get_supervised_topic_training_basis()
            sttb.parse_and_register_training_document("Katze", 'Tiere', 't1')
            sttb.parse_and_register_training_document("Katze", 'Tiere', 't1')

    def test_no_phraselets_after_filtering_error(self):
        with self.assertRaises(NoPhraseletsAfterFilteringError) as context:
            sttb = german_holmes_manager.get_supervised_topic_training_basis(
                oneshot=False)
            sttb.parse_and_register_training_document(
                "Ein Hund jagt eine Katze", 'Tiere1', 't1')
            sttb.parse_and_register_training_document(
                "Ein Hund jagt eine Katze", 'Tiere2', 't2')
            sttb.prepare()
            sttb.train()

    def test_embedding_threshold_too_high(self):
        with self.assertRaises(ValueError) as context:
            m = holmes.Manager('en_core_web_sm', number_of_workers=1)
            m.parse_and_register_document("a")
            coref_holmes_manager.topic_match_documents_against("b",
                                                                                      relation_matching_frequency_threshold=0.75, embedding_matching_frequency_threshold=1.5)

    def test_embedding_threshold_too_low(self):
        with self.assertRaises(ValueError) as context:
            m = holmes.Manager('en_core_web_sm', number_of_workers=1)
            m.parse_and_register_document("a")
            coref_holmes_manager.topic_match_documents_against("b",
                                                                                      relation_matching_frequency_threshold=0.75, embedding_matching_frequency_threshold=-1.5)

    def test_relation_threshold_too_high(self):
        with self.assertRaises(ValueError) as context:
            m = holmes.Manager('en_core_web_sm', number_of_workers=1)
            m.parse_and_register_document("a")
            coref_holmes_manager.topic_match_documents_against("b",
                                                                                      relation_matching_frequency_threshold=1.75, embedding_matching_frequency_threshold=0.5)

    def test_relation_threshold_too_low(self):
        with self.assertRaises(ValueError) as context:
            m = holmes.Manager('en_core_web_sm', number_of_workers=1)
            m.parse_and_register_document("a")
            coref_holmes_manager.topic_match_documents_against("b",
                                                                                      relation_matching_frequency_threshold=-0.75, embedding_matching_frequency_threshold=-0.5)

    def test_embedding_threshold_less_than_relation_threshold(self):
        with self.assertRaises(EmbeddingThresholdLessThanRelationThresholdError) as context:
            m = holmes.Manager('en_core_web_sm', number_of_workers=1)
            m.parse_and_register_document("a")
            coref_holmes_manager.topic_match_documents_against("b",
                                                                                      relation_matching_frequency_threshold=0.75, embedding_matching_frequency_threshold=0.5)

    def test_word_embedding_match_threshold_out_of_range(self):
        with self.assertRaises(ValueError) as context:
            m = holmes.Manager('en_core_web_sm', number_of_workers=1)
            m.parse_and_register_document("a")
            coref_holmes_manager.topic_match_documents_against("b",
                word_embedding_match_threshold=1.2)

    def test_initial_question_word_embedding_match_threshold_out_of_range(self):
        with self.assertRaises(ValueError) as context:
            m = holmes.Manager('en_core_web_sm', number_of_workers=1)
            m.parse_and_register_document("a")
            coref_holmes_manager.topic_match_documents_against("b",
                initial_question_word_embedding_match_threshold=-1.2)

    def test_unrecognized_initial_question_word_behaviour(self):
        with self.assertRaises(ValueError) as context:
            m = holmes.Manager('en_core_web_sm', number_of_workers=1)
            m.parse_and_register_document("a")
            coref_holmes_manager.topic_match_documents_against("b",
                initial_question_word_behaviour='r')
