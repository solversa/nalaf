import abc
import json
import requests
import os
from nala import print_debug
from structures.data import Dataset, Document, Part, Annotation


class Tagger():
    """
    Abstract class for external tagger, like tmVar.
    """
    @abc.abstractmethod
    def generate(self, dataset):
        """
        Generates annotations from an external method, like tmVar or SETH.
        :type nala.structures.Dataset:
        :return: new dataset with annotations
        """
        # get annotated documents from somewhere
        return dataset


class TmVarTagger(Tagger):
    """
    TmVar tagger using the RESTApi from "http://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/tmTools/".
    """
    def generate(self, dataset):
        """
        :param dataset: TODO
        :return:
        """
        # todo docset
        # generate pubtator object using PubtatorWriter
        _tmp_pubtator_send = "temp_pubtator_file.txt"

        # submit to tmtools

        # receive new pubtator object

        # parse to dataset object using TmVarReader

    def generate_abstracts(self, list_of_pmids):
        """
        Generates list of documents using pmids and the restapi interface from tmtools.
        Source: "http://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/tmTools/"
        :param list_of_pmids: strings
        :return nala.structures.Dataset: dataset
        """
        # if os.path.isfile('cache.json'):
        #     tm_var = json.load(open('cache.json'))
        # else:
        url_tmvar = 'http://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/RESTful/tmTool.cgi/Mutation/{0}/JSON/'
        url_converter = 'http://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/'

        # load cache.json if exists
        if os.path.exists('cache.json'):
            with open('cache.json', 'r', encoding='utf-8') as f:
                tm_var = json.load(f)
        else:
            tm_var = {}

        for pmid in list_of_pmids:
            if pmid not in tm_var:  # if pmid was not already downloaded from tmTools
                req = requests.get(url_tmvar.format(pmid))
                try:
                    tm_var[pmid] = req.json()
                except ValueError:
                    pass
        # cache the tmVar annotations so we don't pull them every time
        with open('cache.json', 'w') as file:
            json.dump(tm_var, file, indent=4)

        for key in tm_var:
            print(json.dumps(tm_var[key], indent=4))

        dataset = Dataset()
        for doc_id in list_of_pmids:
            if doc_id in tm_var:
                doc = Document()
                text = tm_var[doc_id]['text']
                part = Part(text)
                denotations = tm_var[doc_id]['denotations']
                annotations = []
                for deno in denotations:
                    ann = Annotation(class_id='e_2', offset=int(deno['span']['begin']), text=text[deno['span']['begin']:deno['span']['end']])
                    annotations.append(ann)
                    # discussion should the annotations from tmvar go to predicted_annotations or annotations?
                part.annotations = annotations
                doc.parts['abstract'] = part
                dataset.documents[doc_id] = doc

        return dataset
