
from workout import Exercise
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivy.uix.screenmanager import Screen
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRectangleFlatButton,MDFlatButton,MDIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.scrollview import ScrollView
from kivymd.uix.list import MDList,OneLineListItem,OneLineIconListItem,BaseListItem
from kivy.storage.jsonstore import JsonStore
from kivymd.uix.toolbar import MDTopAppBar,MDBottomAppBar
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp


class SplitsScreen(MDScreen):

    def __init__(self,manager,store,splitName:str,**kwargs):
        self.screen_manager = manager
        self.store = store
        self.split = splitName
        self.workout_screen = None
        super().__init__(**kwargs)

        self.draw()

    def draw(self):
        self.prepare_main_screen()

    def previous_screen(self,obj):
        self.screen_manager.transition.direction = 'right'
        self.screen_manager.current = self.screen_manager.previous()
        self.screen_manager.remove_widget(self)


    def prepare_main_screen(self):
        self.box = MDBoxLayout(orientation="vertical")

        self.toolbar = MDTopAppBar(title=f"Workout - {self.name}", pos_hint={'top': 1})
        self.toolbar.left_action_items = [["arrow-left", self.previous_screen]]

        self.bottom_menu = MDTopAppBar(title="add split day", pos_hint={'bottom': 1}, elevation=0)
        self.bottom_menu.right_action_items = [["plus", self.show_add_workout_dialog]]


        self.scroll_view = ScrollView()
        self.list = MDList()
        self.scroll_view.add_widget(self.list)

        self.add_widget(self.box)
        self.box.add_widget(self.toolbar)

        self.initialise_split_list()
        self.box.add_widget(self.bottom_menu)

    def initialise_split_list(self):
        try:
            split_dict: dict = self.store["workouts"][self.split]
        except Exception as e:
            self.store["workouts"][self.split] = {}
            self.store.store_sync()
            split_dict = self.store["workouts"][self.split]

        def late_binding_rustler(string: str):
            return lambda: string

        for split in split_dict:
            list_item = OneLineIconListItem(text=split)
            list_item.on_release = lambda workout=late_binding_rustler(split): self.change_screen(workout)
            list_item.add_widget(MDIconButton(icon='delete', pos_hint={'center_x': 0.9, 'center_y': 0.5},
                                              on_release=lambda x, string=late_binding_rustler(
                                                  split): self.show_remove_workout_dialog(string)))
            self.list.add_widget(list_item)

        self.box.add_widget(self.scroll_view)

    def show_add_workout_dialog(self, obj):
        tfield = MDTextField(
            hint_text="Enter split day name",
            max_text_length=50,
            helper_text="use _ instead of spaces"
        )
        dialog = MDDialog(
            title="Add split day",
            type="custom",
            content_cls=tfield,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    text_color=(0, 0, 0, 1),
                    on_release=lambda x: dialog.dismiss()
                ),
                MDFlatButton(
                    text="CONFIRM",
                    theme_text_color="Custom",
                    text_color=(0, 0, 0, 1),
                    on_release=lambda x: self.handle_confirm_button(dialog)
                )
            ]
        )

        dialog.open()

    def handle_confirm_button(self, dialog: MDDialog):
        text = dialog.content_cls.text
        if text is "":
            dialog.dismiss()
            return None
        else:
            splits = self.store["workouts"][self.split].keys()
            if text not in splits:
                self.add_split(text)
                self.store["workouts"][self.name][text] = {}
                # self.store.store_sync()
            else:
                self.show_error("There is already a split day with this name choose another")
            dialog.dismiss()


    def show_error(self,message):
        popup = Popup(title='Error', content=Label(text=message), size_hint=(None, None), size=(400, 200))
        popup.open()

    def add_split(self,split: str):
        '''
        if len(self.list.children) is 0:
            self.list.add_widget(OneLineListItem(text=workout))
            old_child = self.box.children[1]
            self.box.remove_widget(old_child)
            self.box.children.insert(1,self.scroll_view)
        else:
            self.list.add_widget(OneLineListItem(text = workout))
        '''

        list_item = OneLineIconListItem(text=split)
        list_item.on_release = lambda : self.change_screen(lambda:split)
        list_item.add_widget(MDIconButton(icon='delete', pos_hint={'center_x': 0.9, 'center_y': 0.5},on_release=lambda x: self.show_remove_workout_dialog(split)))
        self.list.add_widget(list_item)

    def change_screen(self,split):
        split = split()
        self.workout_screen = WorkoutScreen(self.screen_manager, self.store, split,self.name, name=split)
        self.screen_manager.add_widget(self.workout_screen)
        # self.screen_manager.switch_to(self.split_Screen,duration=0.15)
        self.screen_manager.transition.direction = 'left'
        self.screen_manager.current = split
        pass

    def show_remove_workout_dialog(self,obj):
        split = obj()
        dialog = MDDialog(
            title="Erase Split",
            type="custom",
            content_cls=MDLabel(text="Are you sure you want to erase the split?"),
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    text_color=(0, 0, 0, 1),
                    on_release=lambda x: dialog.dismiss()
                ),
                MDFlatButton(
                    text="CONFIRM",
                    theme_text_color="Custom",
                    text_color=(0, 0, 0, 1),
                    on_release=lambda x: self.delete_split(split,dialog)
                )
            ]
        )

        dialog.open()

    def delete_split(self,split_name,dialog):
        dialog.dismiss()

        def return_text(el):
            return el.text


        split_list: list = self.list.children
        names_list: list[str] = list(map(return_text,split_list))
        index_to_remove = names_list.index(split_name)
        wo_object = self.list.children[index_to_remove]
        self.list.remove_widget(wo_object)

        del self.store["workouts"][self.name][split_name]
        #self.store.store_sync()
        #print(f"{wo_name} deleted")

class WorkoutScreen(MDScreen):

    def __init__(self, manager, store, day_name: str,split_name:str, **kwargs):
        self.screen_manager = manager
        self.store = store
        self.split_name = split_name
        super().__init__(**kwargs)

        self.draw()
        #self.draw()


    def draw(self):
        self.prepare_main_screen()

    def previous_screen(self, obj):
        self.screen_manager.transition.direction = 'right'
        self.screen_manager.current = self.screen_manager.previous()
        self.screen_manager.remove_widget(self)

    def prepare_main_screen(self):
        self.box = MDBoxLayout(orientation="vertical")

        self.toolbar = MDTopAppBar(title=f"Exercises - {self.name}", pos_hint={'top': 1})
        self.toolbar.left_action_items = [["arrow-left", self.previous_screen]]

        self.bottom_menu = MDTopAppBar(title="add exercise", pos_hint={'bottom': 1}, elevation=0)
        self.bottom_menu.right_action_items = [["plus", self.show_add_exercise_dialog]]

        self.scroll_view = ScrollView()
        self.list = MDList()
        self.scroll_view.add_widget(self.list)

        self.add_widget(self.box)
        self.box.add_widget(self.toolbar)

        self.initialise_workout_day_list()
        self.box.add_widget(self.bottom_menu)

    def initialise_workout_day_list(self):

        try:
            exercise_dict: dict = self.store["workouts"][self.split_name][self.name]
        except Exception as e:
            self.store["workouts"][self.split_name][self.name] = {}
            self.store.store_sync()
            exercise_dict = self.store["workouts"][self.split_name][self.name]

        def late_binding_rustler(string: str):
            return lambda: string

        for exercise in exercise_dict:
            list_item = OneLineIconListItem(text=exercise)
            list_item.on_release = lambda workout=late_binding_rustler(exercise): self.change_screen(workout)
            list_item.add_widget(MDIconButton(icon='delete', pos_hint={'center_x': 0.9, 'center_y': 0.5},
                                              on_release=lambda x, string=late_binding_rustler(
                                                  exercise): self.show_remove_exercise_dialog(string)))
            self.list.add_widget(list_item)
        


        self.box.add_widget(self.scroll_view)


    def show_add_exercise_dialog(self, obj):
        tfield = MDTextField(
            hint_text="Enter exercise name",
            max_text_length=50,
            helper_text="use _ instead of spaces"
        )
        dialog = MDDialog(
            title="Add exercise",
            type="custom",
            content_cls=tfield,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    text_color=(0, 0, 0, 1),
                    on_release=lambda x: dialog.dismiss()
                ),
                MDFlatButton(
                    text="CONFIRM",
                    theme_text_color="Custom",
                    text_color=(0, 0, 0, 1),
                    on_release=lambda x: self.handle_confirm_button(dialog)
                )
            ]
        )

        dialog.open()

    def handle_confirm_button(self, dialog: MDDialog):
        text = dialog.content_cls.text
        if text is "":
            dialog.dismiss()
            return None
        else:
            exercises = self.store["workouts"][self.split_name][self.name].keys()
            if text not in exercises:
                self.add_exercise(text)
                self.store["workouts"][self.split_name][self.name][text] = {}
                # self.store.store_sync()
            else:
                self.show_error("There is already an exercise with this name choose another")
            dialog.dismiss()

    def show_error(self, message):
        popup = Popup(title='Error', content=Label(text=message), size_hint=(None, None), size=(400, 200))
        popup.open()

    def add_exercise(self, exercise: str):
        '''
        if len(self.list.children) is 0:
            self.list.add_widget(OneLineListItem(text=exercise))
            old_child = self.box.children[1]
            self.box.remove_widget(old_child)
            self.box.children.insert(1,self.scroll_view)
        else:
            self.list.add_widget(OneLineListItem(text = exercise))

        '''

        list_item = OneLineIconListItem(text=exercise)
        list_item.on_release = lambda: self.change_screen(lambda: exercise)
        list_item.add_widget(MDIconButton(icon='delete', pos_hint={'center_x': 0.9, 'center_y': 0.5},
                                          on_release=lambda x: self.show_remove_workout_dialog(exercise)))

        self.list.add_widget(list_item)

    def change_screen(self, exercise):
        exercise = exercise()
        path=["workouts",self.split_name,self.name,exercise]
        self.split_Screen = ExerciseScreen(self.screen_manager, self.store, exercise,path, name=exercise)
        self.screen_manager.add_widget(self.split_Screen)
        self.screen_manager.transition.direction = 'left'
        # self.screen_manager.switch_to(self.split_Screen,duration=0.15)
        self.screen_manager.current = exercise

    def show_remove_exercise_dialog(self, obj):
        split = obj()
        dialog = MDDialog(
            title="Erase exercise",
            type="custom",
            content_cls=MDLabel(text="Are you sure you want to erase the exercise?"),
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    text_color=(0, 0, 0, 1),
                    on_release=lambda x: dialog.dismiss()
                ),
                MDFlatButton(
                    text="CONFIRM",
                    theme_text_color="Custom",
                    text_color=(0, 0, 0, 1),
                    on_release=lambda x: self.delete_exercise(split, dialog)
                )
            ]
        )

        dialog.open()

    def delete_exercise(self, exercise_name, dialog):
        dialog.dismiss()

        def return_text(el):
            return el.text

        ex_list: list = self.list.children
        names_list: list[str] = list(map(return_text, ex_list))
        index_to_remove = names_list.index(exercise_name)
        wo_object = self.list.children[index_to_remove]
        self.list.remove_widget(wo_object)

        del self.store["workouts"][self.split_name][self.name][exercise_name]
        # self.store.store_sync()
        # print(f"{wo_name} deleted")


class ExerciseScreen(MDScreen):

    def __init__(self, manager, store,exercise_name: str,path, **kwargs):
        self.screen_manager = manager
        self.store = store
        self.exercise_name = exercise_name
        self.exercise_obj = None
        self.path = path
        super().__init__(**kwargs)

        self.draw()
        # self.draw()

    def draw(self):
        self.prepare_main_screen()

    def prepare_main_screen(self):
        self.box = MDBoxLayout(orientation="vertical")

        self.toolbar = MDTopAppBar(title=f"Exercise - {self.name}", pos_hint={'top': 1})
        self.toolbar.left_action_items = [["arrow-left", self.previous_screen]]

        self.bottom_menu = MDTopAppBar(title="Save exercise data", pos_hint={'bottom': 1}, elevation=0)
        self.bottom_menu.right_action_items = [["content-save-check", self.save_exercise_data]]

        self.scroll_view = ScrollView()
        self.list = MDList()
        self.scroll_view.add_widget(self.list)

        self.add_widget(self.box)
        self.box.add_widget(self.toolbar)

        self.exercise_obj = Exercise(self.name,self.store,self.path.copy())
        self.box.add_widget(self.exercise_obj.get_exercise())
        #self.initialise_workout_day_list()

        self.box.add_widget(self.bottom_menu)

    def previous_screen(self,obj):

        self.screen_manager.transition.direction = 'right'
        self.screen_manager.current = self.screen_manager.previous()
        self.screen_manager.remove_widget(self)

    def save_exercise_data(self,obj):

        try:
            #self.store["workouts"]["ppl"]["push"][self.name]
            sets = self.exercise_obj.get_sets_list()
            self.store[self.path[0]][self.path[1]][self.path[2]][self.path[3]] = sets
        except Exception as e:
            self.show_popup(
                title="Error",
                message=f"Could not save exercise data:{e}"
            )
            return

        self.show_popup(
                title="Data saved successfully",
                message="the reps and weight of this exercises have been updated successfully"
        )


    def show_popup(self, title,message):
        label = MDLabel(text=message,
                        halign="center",  # Horizontal alignment
                        valign="middle",  # Vertical alignment
                        theme_text_color="Custom",
                        text_color=(1, 1,1, 1))

        popup = Popup(title=title, content=label, size_hint=(0.8, 0.3))

        popup.open()

