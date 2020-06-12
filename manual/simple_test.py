from jupydoc import DocPublisher

__docs__ = ['Simple']

class Simple(DocPublisher):
    """
    title: Development
    abstract: This ia a very basic class
    
    sections: 
          section1 section2
    subsections:
        section1: sub1 sub2

    """

    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        pass
    
    def section1(self):
        """First Section 
        
        """
        r = 1/3
        self.publishme()

    def sub1(self):
        """First Subsection

        r={r:.2f}
        """
        self.publishme()
        
    def sub2(self):
        """Second subsection
        """
        self.publishme()

    def section2(self):
        """Second Section
        """
        self.publishme()