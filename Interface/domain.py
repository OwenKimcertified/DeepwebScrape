from enum import Enum

class AnalyzerType(str, Enum):
    RANSOMWARE = "ransomware"
    FORUM_USER = "forum_user"
    FORUM_POST = "forum_post"

class DomainInfo(Enum):
    AKIRA = ("akiral2iz6a7qgd3ayp3l6yub7xx2uep76idk3u2kollpj5z3z636bad.onion", AnalyzerType.RANSOMWARE, "AKIRA")
    CUBA = ("cuba4ikm4jakjgmkezytyawtdgr2xymvy6nvzgw5cglswg3si76icnqd.onion", AnalyzerType.RANSOMWARE, "Cuba")
    PLAY = ("mbrlkbtq5jonaqkurjwmxftytyn2ethqvbxfu4rgjbkkknndqwae6byd.onion", AnalyzerType.RANSOMWARE, "PLAY")
    BREACHED_USER = ("breachedu76kdyavc6szj6ppbplfqoz3pgrk3zw57my4vybgblpfeayd.onion", AnalyzerType.FORUM_USER, "Breached")
    BREACHED_POST = ("breachedu76kdyavc6szj6ppbplfqoz3pgrk3zw57my4vybgblpfeayd.onion", AnalyzerType.FORUM_POST, "Breached")