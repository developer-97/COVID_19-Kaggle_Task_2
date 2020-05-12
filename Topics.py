import random

class Topics:
    def __init__(self):
        self=self

    def populateTopics(self):
        topics = []
        topics.append(['hospitalized', 'children', 'rhinovirus', 'syncytial', 'respiratory', 'pneumoniae', 'rsv',
                           'pneumonia', 'multiplex', 'tract'])

        topics.append(['moi', 'transfected', 'transfection', 'luciferase', 'knockdown', 'seeded', 'flag', 'mock',
                           'a549', 'lysates'])

        topics.append(['health', 'public', 'services', 'government', 'policy', 'education', 'resources',
                           'international', 'issues', 'preparedness'])

        topics.append(['parameter', 'probability', 'simulations', 'distributions', 'dynamics', 'epidemic',
                           'spatial', 'parameters', 'dataset', 'simulation'])

        topics.append(['hospitalization', 'cohort', 'ci', 'pulmonary', 'patients', 'admission', 'pneumonia',
                           'hospital', 'severity', 'trial'])

        topics.append(['amplification', 'primers', 'primer', 'nucleic', 'pcr', 'copies', 'genbank', 'probe',
                           'extraction', 'amplified'])

        topics.append(['residues', 'hydrophobic', 'conformation', 'mutant', 'residue', 'terminus', 'nacl',
                           'terminal', 'mutants', 'crystal'])

        topics.append(['genomes', 'sequences', 'phylogenetic', 'sequence', 'alignment', 'codons', 'similarity',
                           'ncbi', 'genome', 'nucleotide'])

        topics.append(['kinase', 'activate', 'activation', 'signaling', 'dendritic', 'degradation', 'receptors',
                           'activated', 'inducing', 'innate'])

        topics.append(['zoonotic', 'humans', 'international', 'africa', 'emerging', 'countries', 'risks',
                           'livestock', 'world', 'global'])

        topics.append(['neutralizing', 'elisa', 'sera', 'immunized', 'plates', 'coated', 'igg', 'antibody',
                            'epitopes', 'mabs'])

        topics.append(['assumed', 'epidemic', 'estimates', 'estimate', 'spatial', 'social', 'probability',
                            'parameter', 'simulation', 'scenario'])

        topics.append(['mice', 'il', 'cd8', 'cytokine', 'bd', 'cytokines', 'infiltration', 'cd4', 'lungs',
                            'inflammatory'])
        return topics

    def startingTopics(self):
        return ['inflammatory','epidemic','antibody','risks','activation','genomes','mutant','extraction',
                'pulmonary','dynamics','government','moi','respiratory']


    def recommendedTopics(self,keyword):
        recommendations = []
        for topic in self.populateTopics():
            bagOfTerms = [i for i in range(len(topic)) if topic[i] is not keyword]
            if keyword in topic:
                recommendations.append(topic[bagOfTerms.pop(int(random.random()*len(topic)-1))])
                recommendations.append(topic[bagOfTerms.pop(int(random.random()*len(topic))-1)])
                recommendations.append(topic[bagOfTerms.pop(int(random.random()*len(topic))-1)])
        return recommendations