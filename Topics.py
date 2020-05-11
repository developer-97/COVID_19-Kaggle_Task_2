import random
class Topics:
    def populateTopics(self):
        topics = {}
        topics[0] = ['hospitalized', 'children', 'rhinovirus', 'syncytial', 'respiratory', 'pneumoniae', 'rsv',
                           'pneumonia', 'multiplex', 'tract']

        topics[1] = ['moi', 'transfected', 'transfection', 'luciferase', 'knockdown', 'seeded', 'flag', 'mock',
                           'a549', 'lysates']

        topics[2] = ['health', 'public', 'services', 'government', 'policy', 'education', 'resources',
                           'international', 'issues', 'preparedness']

        topics[3] = ['parameter', 'probability', 'simulations', 'distributions', 'dynamics', 'epidemic',
                           'spatial', 'parameters', 'dataset', 'simulation']

        topics[4] = ['hospitalization', 'cohort', 'ci', 'pulmonary', 'patients', 'admission', 'pneumonia',
                           'hospital', 'severity', 'trial']

        topics[5] = ['amplification', 'primers', 'primer', 'nucleic', 'pcr', 'copies', 'genbank', 'probe',
                           'extraction', 'amplified']

        topics[6] = ['residues', 'hydrophobic', 'conformation', 'mutant', 'residue', 'terminus', 'nacl',
                           'terminal', 'mutants', 'crystal']

        topics[7] = ['genomes', 'sequences', 'phylogenetic', 'sequence', 'alignment', 'codons', 'similarity',
                           'ncbi', 'genome', 'nucleotide']

        topics[8] = ['kinase', 'activate', 'activation', 'signaling', 'dendritic', 'degradation', 'receptors',
                           'activated', 'inducing', 'innate']

        topics[9] = ['zoonotic', 'humans', 'international', 'africa', 'emerging', 'countries', 'risks',
                           'livestock', 'world', 'global']

        topics[10] = ['neutralizing', 'elisa', 'sera', 'immunized', 'plates', 'coated', 'igg', 'antibody',
                            'epitopes', 'mabs']

        topics[11] = ['assumed', 'epidemic', 'estimates', 'estimate', 'spatial', 'social', 'probability',
                            'parameter', 'simulation', 'scenario']

        topics[12] = ['mice', 'il', 'cd8', 'cytokine', 'bd', 'cytokines', 'infiltration', 'cd4', 'lungs',
                            'inflammatory']
        return topics

    def startingTopics(self):
        return ['inflammatory','epidemic','antibody','risks','activation','genomes','mutant','extraction',
                'pulmonary','dynamics','government','moi','respiratory']


    def recommendedTopics(self, keyword):
        recommendations = []
        for topic in self.topics:
            if keyword in topic:
                recommendations.append(topic[random.random()*len(topic)])
                recommendations.append(topic[random.random() * len(topic)])
                recommendations.append(topic[random.random() * len(topic)])
        return recommendations

    def __init__(self):
        self.topics = self.populateTopics()