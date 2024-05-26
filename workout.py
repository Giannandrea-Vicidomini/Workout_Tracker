from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import ScrollView
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDIconButton
from kivy.uix.popup import Popup

class Exercise:

    def __init__(self,exercise_name:str,store,path):
        self.exercise_name = exercise_name
        self.store = store
        self.table_body = None
        self.path = path
        self.construct_exercise_widget()

        pass


    def construct_exercise_widget(self):
        sets = None
        try:
            sets =self.store[self.path[0]][self.path[1]][self.path[2]][self.path[3]]

        except Exception as e:
            self.store[self.path[0]][self.path[1]][self.path[2]][self.path[3]]=[]
            sets = self.store[self.path[0]][self.path[1]][self.path[2]][self.path[3]]


        btn_container =MDFloatLayout()
        add_button = MDIconButton(
            icon="plus",
            theme_text_color="Custom",
            text_color=(0, 0, 1, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            valign="center",
            halign="center",
            on_release = lambda obj: self.add_card(obj)
        )
        btn_container.add_widget(add_button)
        scroll = ScrollView()
        grid = MDGridLayout(cols=1,
                            size_hint_y=None,
                            spacing = "20dp",
                            padding= "20dp"
                            )
        grid.height = grid.minimum_height
        grid.width = grid.minimum_width
        if len(sets) == 0:
            for i in range(1):
                grid.add_widget(self.create_card())
        else:
            for reps,weight in sets:
                grid.add_widget(self.create_card(reps,weight))

        grid.add_widget(btn_container)
        scroll.add_widget(grid)
        self.table_body = scroll


    def create_card(self,reps='',weight=''):
        card = MDCard(
            orientation = "horizontal",
            padding = "8dp",
            size_hint = (1,None),
            elevation = 5
        )
        content = self.__create_card_body(reps,weight)
        card.add_widget(content)

        return card

    def get_exercise(self):
        return self.table_body

    def __create_card_body(self,reps,weight):

        body = MDBoxLayout(orientation = "horizontal")
        box1 = MDBoxLayout(orientation="vertical")
        box2 = MDBoxLayout(orientation="vertical")
        box3 = MDBoxLayout(orientation="vertical")

        reps_label = MDLabel(text = "reps",halign="center",valign="center")
        reps_field = MDTextField(
            size_hint_x=0.3,
            width=300,
            halign="center",
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        reps_field.text = reps

        weight_label = MDLabel(text="Kg",halign="center",valign="center")
        weight_field= MDTextField(
            size_hint_x=0.3,
            width=300,
            halign="center",
            pos_hint={"center_x": 0.5, "center_y": 0.5}

        )
        weight_field.text = weight

        erase_button = MDIconButton(
            icon="trash-can",
            theme_text_color="Custom",
            text_color=(0, 0, 0, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            valign = "center",
            on_release = lambda obj : self.erase_card(obj)
        )

        box1.add_widget(reps_label)
        box1.add_widget(reps_field)
        box2.add_widget(weight_label)
        box2.add_widget(weight_field)
        box3.add_widget(erase_button)

        body.add_widget(box1)
        body.add_widget(box2)
        body.add_widget(box3)
        return body

    def erase_card(self,obj):
        card = obj.parent.parent.parent
        card_grid = self.table_body.children[0]

        if len(card_grid.children) == 2:
            self.show_popup(title= "Error",message= "An exercise must have at least one set.")
            return

        card_grid.remove_widget(card)

    def add_card(self,obj):
        card = self.create_card()
        card_grid = self.table_body.children[0]
        add_button = card_grid.children[len(self.table_body.children)-1]
        card_grid.remove_widget(add_button)
        card_grid.add_widget(card)
        card_grid.add_widget(add_button)

    def show_popup(self, title, message):
        label = MDLabel(text=message,
                        halign="center",  # Horizontal alignment
                        valign="middle",  # Vertical alignment
                        theme_text_color="Custom",
                        text_color=(1, 1, 1, 1))

        popup = Popup(title=title, content=label, size_hint=(0.8, 0.3))

        popup.open()


    def get_sets_list(self):
        exercise_table = self.table_body.children[0]
        sets = [self.__get_card_text_fields(card) for card in exercise_table.children[1:]]
        sets.reverse()
        return sets



    def __get_card_text_fields(self,card:MDCard):
        reps_field = card.children[0].children[2].children[0].text
        weight_field = card.children[0].children[1].children[0].text
        return [reps_field,weight_field]
