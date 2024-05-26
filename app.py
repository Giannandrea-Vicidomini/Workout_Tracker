from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRectangleFlatButton,MDFlatButton,MDIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.scrollview import ScrollView
from kivymd.uix.list import MDList,OneLineListItem,OneLineIconListItem
from kivy.storage.jsonstore import JsonStore
from kivymd.uix.toolbar import MDTopAppBar,MDBottomAppBar
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager,Screen
from utils import WorkoutScreen,SplitsScreen
from kivymd.uix.navigationdrawer import MDNavigationDrawer
from kivy.uix.image import Image

class DemoApp(MDApp):

    def on_stop(self):
        print(self.store)
        self.store.store_sync()

    def build(self):

        self.split_Screen = None
        self.store = JsonStore("workout.json")
        self.screen_manager = ScreenManager()
        self.prepare_main_screen()
        self.screen_manager.add_widget(self.screen)
        return self.screen_manager

    def initialise_wo_list(self):
        try:
            wo_dict: dict = self.store["workouts"]
        except Exception as e:
            self.store["workouts"] = {}
            self.store.store_sync()
            wo_dict = self.store["workouts"]

        def late_binding_rustler(string:str):
            return lambda: string

        for wo in wo_dict:

            list_item = OneLineIconListItem(text=wo)
            list_item.on_release = lambda workout = late_binding_rustler(wo) : self.change_screen(workout)
            list_item.add_widget(MDIconButton(icon='delete', pos_hint={'center_x': 0.9, 'center_y': 0.5},on_release=lambda x, string= late_binding_rustler(wo): self.show_remove_workout_dialog(string)))
            self.list.add_widget(list_item)

        self.box.add_widget(self.scroll_view)

    def add_workout(self,workout: str):
        '''
        if len(self.list.children) is 0:
            self.list.add_widget(OneLineListItem(text=workout))
            old_child = self.box.children[1]
            self.box.remove_widget(old_child)
            self.box.children.insert(1,self.scroll_view)
        else:
            self.list.add_widget(OneLineListItem(text = workout))
        '''

        list_item = OneLineIconListItem(text=workout)
        list_item.on_release = lambda : self.change_screen(lambda:workout)
        list_item.add_widget(MDIconButton(icon='delete', pos_hint={'center_x': 0.9, 'center_y': 0.5},on_release=lambda x: self.show_remove_workout_dialog(workout)))
        self.list.add_widget(list_item)

    def delete_workout(self,wo_name,dialog):
        dialog.dismiss()

        def return_text(el):
            return el.text


        wo_list: list = self.list.children
        names_list: list[str] = list(map(return_text,wo_list))
        index_to_remove = names_list.index(wo_name)
        wo_object = self.list.children[index_to_remove]
        self.list.remove_widget(wo_object)

        del self.store["workouts"][wo_name]
        #self.store.store_sync()
        #print(f"{wo_name} deleted")

    def change_screen(self,workout):
        workout  = workout()
        self.split_Screen = SplitsScreen(self.screen_manager,self.store,workout,name = workout)
        self.screen_manager.add_widget(self.split_Screen)
        self.screen_manager.transition.direction = 'left'
        #self.screen_manager.switch_to(self.split_Screen,duration=0.15)
        self.screen_manager.current = workout

    def show_remove_workout_dialog(self,obj):
        workout = obj()
        dialog = MDDialog(
            title="Erase Workout",
            type="custom",
            content_cls=MDLabel(text="Are you sure you want to erase the workout?"),
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
                    on_release=lambda x: self.delete_workout(workout,dialog)
                )
            ]
        )

        dialog.open()
    def show_add_workout_dialog(self,obj):

        tfield = MDTextField(
                hint_text="Enter workout name",
                max_text_length=50,
                helper_text="use _ instead of spaces"
        )
        dialog = MDDialog(
            title="Add Workout",
            type="custom",
            content_cls=tfield,
            buttons = [
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    text_color=(0,0,0,1),
                    on_release=lambda x: dialog.dismiss()
                ),
                MDFlatButton(
                    text="CONFIRM",
                    theme_text_color="Custom",
                    text_color=(0,0,0,1),
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
            work_outs = self.store["workouts"].keys()
            if text not in work_outs:
                self.add_workout(text)
                self.store["workouts"][text] = {}
                #self.store.store_sync()
            else:
                self.show_error("There is already a workout with this name choose another")
            dialog.dismiss()

    def show_error(self,message):
        popup = Popup(title='Error', content=Label(text=message), size_hint=(None, None), size=(400, 200))
        popup.open()

    def prepare_main_screen(self):

        self.navigation_drawer = MDNavigationDrawer(radius=[0, 0, 0, 0])
        self.prepare_navigation_drawer()

        self.box = MDBoxLayout(orientation="vertical")

        self.toolbar = MDTopAppBar(title="Workout Manager", pos_hint={'top': 1})
        self.toolbar.left_action_items = [["menu",lambda x: self.navigation_drawer.set_state("open") ]]

        self.bottom_menu = MDTopAppBar(title="add workout", pos_hint={'bottom': 1}, elevation=0)
        self.bottom_menu.right_action_items = [["plus", self.show_add_workout_dialog]]

        self.screen = MDScreen(name="Main_Screen")
        self.store = JsonStore("workout.json")

        self.scroll_view = ScrollView()
        self.list = MDList()
        self.scroll_view.add_widget(self.list)

        self.screen.add_widget(self.box)
        self.box.add_widget(self.toolbar)

        self.initialise_wo_list()
        self.box.add_widget(self.bottom_menu)

        self.screen.add_widget(self.navigation_drawer)

    def prepare_navigation_drawer(self):

        main = MDBoxLayout(orientation="vertical",spacing = "8dp")
        scroll_pane = ScrollView()
        list = MDList()
        gif = Image(
            source= "assets\\kitten2.gif",
            allow_stretch= True
        )


        list.add_widget(
            OneLineIconListItem(
                text= "Weight tracker",
                on_release = lambda obj: self.weigh_tracker_screen(obj)
            )

        )
        list.add_widget(
            OneLineIconListItem(
                text="Chatbot",
                on_release=lambda obj: self.chatbot_screen(obj)
            )

        )
        scroll_pane.add_widget(list)
        main.add_widget(gif)
        gif.center = gif.parent.center
        main.add_widget(scroll_pane)
        self.navigation_drawer.add_widget(main)

    def chatbot_screen(self,obj):
        print(obj)
        pass

    def weigh_tracker_screen(self,obj):
        print(obj)
        pass