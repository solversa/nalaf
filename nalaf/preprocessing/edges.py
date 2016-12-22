import abc
from nalaf.structures.data import Edge
from itertools import product, chain


class EdgeGenerator(object):
    """
    Abstract class for generating edges between two entities. Each edge represents
    a possible relationship between the two entities
    Subclasses that inherit this class should:
    * Be named [Name]EdgeGenerator
    * Implement the abstract method generate
    * Append new items to the list field "edges" of each Part in the dataset
    """

    def __init__(self, entity1_class, entity2_class, relation_type):
        self.entity1_class = entity1_class
        self.entity2_class = entity2_class
        self.relation_type = relation_type


    @abc.abstractmethod
    def generate(self, dataset):
        """
        :type dataset: nalaf.structures.data.Dataset
        """
        return


class SentenceDistanceEdgeGenerator(EdgeGenerator):
    """
    Simple implementation of generating edges between the two entities
    if they are #`distance` sentences away (always same part).

    As a special case, if `distance` is None, the distance is disregarded,
    consequently creating edges for all entities within a part (paragraph or what not).
    """

    def __init__(self, entity1_class, entity2_class, relation_type, distance, use_predicted_entities=True, rewrite_edges=True):
        # Note: would be nice to implement the word filter too here -- see below

        super().__init__(entity1_class, entity2_class, relation_type)
        self.distance = distance
        self.use_predicted_entities = use_predicted_entities
        self.rewrite_edges = rewrite_edges

        self.part_entities = (lambda part: chain(part.annotations, part.predicted_annotations) if self.use_predicted_entities else part.annotations)


    def generate(self, dataset):

        for part in dataset.parts():
            if self.rewrite_edges:
                part.edges = []

            for e_1, e_2 in product(
                    (e for e in self.part_entities(part) if e.class_id == self.entity1_class),
                    (e for e in self.part_entities(part) if e.class_id == self.entity2_class)):

                s1_index = part.get_sentence_index_for_annotation(e_1)
                s2_index = part.get_sentence_index_for_annotation(e_2)

                if s2_index < s1_index:
                    s1_index, s2_index = s2_index, s1_index

                if e_2.offset < e_1.offset:
                    e_1, e_2 = e_2, e_1

                pair_distance = s2_index - s1_index
                assert pair_distance >= 0  # Because they must be sorted

                if pair_distance == self.distance or self.distance is None:
                    edge = Edge(self.relation_type, e_1, e_2, part, part, s1_index, s2_index)
                    part.edges.append(edge)


class CombinatorEdgeGenerator(EdgeGenerator):
    """
    Combines 2 or more edge generators.

    Assumes (does not test) that all generators have same entities and relation types properties.
    """

    def __init__(self, generator_1, generator_2, *rest):
        super().__init__(generator_1.entity1_class, generator_1.entity2_class, generator_1.relation_type)
        self.generators = [generator_1, generator_2, *rest]


    def generate(self, dataset):
        for g in self.generators:
            g.generate(dataset)


class WordFilterEdgeGenerator(EdgeGenerator):
    """
    Simple implementation of generating edges between the two entities
    if they are contained in the same sentence AND the sentence
    contains one of the trigger-like given words

    **It only uses the _gold_ annotations**

    """

    def __init__(self, entity1_class, entity2_class, relation_type, words):
        super().__init__(entity1_class, entity2_class, relation_type)
        self.words = words


    def generate(self, dataset):
        from itertools import product

        for part in dataset.parts():
            part.edges = []

            for ann_1, ann_2 in product(
                    (ann for ann in part.annotations if ann.class_id == self.entity1_class),
                    (ann for ann in part.annotations if ann.class_id == self.entity2_class)):

                index_1 = part.get_sentence_index_for_annotation(ann_1)
                index_2 = part.get_sentence_index_for_annotation(ann_2)

                if index_1 == index_2 and index_1 is not None:

                    for token in part.sentences[index_1]:

                        if token.word in self.words:
                            edge = Edge(self.relation_type, ann_1, ann_2, part, part, index_1, index_2)

                            part.edges.append(edge)

                            break
