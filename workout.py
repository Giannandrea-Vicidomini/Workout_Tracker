from kivymd.uix.gridlayout import GridLayout
from kivymd.uix.scrollview import ScrollView
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel

class Exercise:

    def __init__(self,exercise_name:str,n_sets:int,n_reps:int):
        self.exercise_name = exercise_name
        self.n_sets = n_sets
        self.n_reps = n_reps
        self.table_body = None
        self.construt_exercise_widget()
        pass


    def construt_exercise_widget(self):
        scroll = ScrollView()
        grid = GridLayout(cols=1, size_hint_y=None, spacing = "20dp",padding= "20dp")
        grid.height = grid.minimum_height
        grid.width = grid.minimum_width
        for i in range(5):
            grid.add_widget(self.create_card())
        scroll.add_widget(grid)
        self.table_body = scroll


    def create_card(self):
        card = MDCard(
            orientation = "horizontal",
            padding = "8dp",
            size_hint = (1,None),
            elevation = 5
        )

        card.add_widget(MDLabel(text= "i'm a row"))

        return card

    def get_exercise(self):
        return self.table_body
