"""
Reference: Volcano—An Extensible and Parallel Query Evaluation System (Graefe, 1990)
Base interface for all physical plan nodes enforcing the Pull-Based Iterator Model.
"""
class Executor:
    def init(self):
        pass
    def next(self):
        pass
