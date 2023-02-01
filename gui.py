import dearpygui.dearpygui as dpg
import helper as h
import webbrowser
from config import *
import random, time, overlay, ctypes

class GUI(Config):
    def __init__(self) -> None:
        self.random_string = self.get_random_string()
        self.config = Config()
        
    def get_random_string(self) -> None:
        chars = ['A',
        'B', 'C', 'D', 'E', 'F','G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'U', 'P', 'R', 'S', 'T', 'W', 'Y', 'Z',
        'a', 'b', 'c', 'd', 'e', 'f','g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'u', 'p', 'r', 's', 't', 'w', 'y', 'z',
        '1','2', '3', '4', '5', '6', '7', '8', '9', '0', '!', '@', '#', '$', '%', '^', '&', '&', '(', ')', '-', '_', '=', '+']
        return ''.join(random.choice(chars) for _ in range(0, 15))
    
    def _log(self, sender, app_data, user_data):
        print(f"sender: {sender}, \t app_data: {app_data}, \t user_data: {user_data}")

    def init_menu(self):
        dpg.create_context()
        dpg.create_viewport(title=self.random_string, decorated=True, width=380, height=150)
        self.config.create_default_config('default_config.json')
        with dpg.window(tag='w_main'):
            

                
                
            with dpg.collapsing_header(label='Overlay', tag='overlay_header'):
   
                dpg.add_checkbox(label='Head Indicator', tag='c_head_indicator')
                dpg.add_checkbox(label='Bomb Indicator', tag='c_bomb_indicator')
                dpg.add_checkbox(label='Grenade Trajectory', tag='c_gre_line')
                dpg.add_checkbox(label='Sniper Crosshair', tag='c_sniper_crosshair')
                dpg.add_checkbox(label='Recoil Crosshair', tag='c_recoil_crosshair')
                dpg.add_separator()
            with dpg.collapsing_header(label='Misc', tag='misc_header'):
                dpg.add_checkbox(label='Auto Pistol', tag='c_autopistol', default_value=True)
                dpg.add_combo(label='Key', items=tuple(h.gui_keys_list.keys()), default_value='LEFT MOUSE', width=215, tag='k_autopistol')
                dpg.add_checkbox(label='BunnyHop', tag='c_bh')
                dpg.add_checkbox(label='Auto Strafer', tag='c_strafer')
                dpg.add_checkbox(label='Auto Zeus', tag='c_zeus')
                dpg.add_checkbox(label='Knife Bot', tag='c_knifebot')
       
                dpg.add_checkbox(label='Show FPS', tag='c_fps')

    

                
            dpg.add_separator()
            dpg.add_button(label='Unload', width=160, height=25, tag='b_unload')
        
            dpg.add_text('Laplused Extra - Version: 2.3', color=(255, 0, 0, 255))
            dpg.add_slider_float(label='Third Person View', default_value=150.0, min_value=100.0, max_value=200.0, width=215, tag='c_thirdperson')
            #dpg.add_slider_float(label='Extra Punch', default_value=0.055, min_value=0.0, max_value=1.0, width=215, tag='view_extra_punch')
            
            
            
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("w_main", True)
        
    def make_interactive(self):
        while True:
            try:
                dpg.hide_item('k_autopistol') if dpg.get_value('c_autopistol') == False else dpg.show_item('k_autopistol')
                dpg.hide_item('c_strafer') if dpg.get_value('c_bh') == False else dpg.show_item('c_strafer')
                dpg.configure_item('c_config_list', items=tuple(self.config.get_config_list()))
            except Exception as err:
                pass
            time.sleep(0.01)
            
    def create_config(self):
        if dpg.get_value('i_config_name') != '':
            config_file = f"{dpg.get_value('i_config_name')}"
            path_to_config = f'{self.config.get_cfg_dir}\\'+ f'{config_file}'
            try:
                if os.path.exists(f'{path_to_config}.json'):
                    ctypes.windll.user32.MessageBoxW(0, 'Config file with the same name already exist!', 'Config Error', 0)
                else:
                    with open(f'{path_to_config}.json', 'w+') as file:
                        file.write(json.dumps(config_example))
            except Exception as err:
                pass
            
    def save_config(self):
        if dpg.get_value('c_config_list') != '':
            config_file = f"{dpg.get_value('c_config_list')}.json"
            path_to_config = (f'{self.config.get_cfg_dir}\\'+ f'{config_file}')
            with open(f'{path_to_config}', 'r+') as f:
                content = json.load(f)
                # os.system('cls')
                # print(path_to_config, '\n', content)
                # save new values
                           
                content['overlay']['head_indicator'] = dpg.get_value('c_head_indicator')
                content['overlay']['bomb_indicator'] = dpg.get_value('c_bomb_indicator')
                content['overlay']['grenade_traces'] = dpg.get_value('c_gre_line')
                content['overlay']['sniper_crosshair'] = dpg.get_value('c_sniper_crosshair')
                content['overlay']['recoil_crosshair'] = dpg.get_value('c_recoil_crosshair')
                
                content['misc']['auto_pistol'] = dpg.get_value('c_autopistol')
                content['misc']['auto_pistol_key'] = dpg.get_value('k_autopistol')
                content['misc']['bunny_hop'] = dpg.get_value('c_bh')
                content['misc']['auto_strafe'] = dpg.get_value('c_strafer')
                content['misc']['auto_zeus'] = dpg.get_value('c_zeus')
                content['misc']['knife_bot'] = dpg.get_value('c_knifebot')

    
                
                with open(f'{path_to_config}', 'w') as f:
                    json.dump(content, f)
        
    # TO:DO Clean up
    def load_config(self):
        config = f"{dpg.get_value('c_config_list')}.json"
        path_to_config = (f'{self.config.get_cfg_dir}\\'+ f'{config}')
        config_name = dpg.get_value('c_config_list')
        # print(path_to_config)
        if dpg.get_value('c_config_list') == '.json':
            ctypes.windll.user32.MessageBoxW(0, 'Could not load given config!', 'Config Error', 0)
        else:
           
                    
           
            dpg.set_value('c_head_indicator', self.config.read_value(config_name, 'overlay','head_indicator'))
            dpg.set_value('c_bomb_indicator', self.config.read_value(config_name, 'overlay','bomb_indicator'))
            dpg.set_value('c_gre_line', self.config.read_value(config_name, 'overlay','grenade_traces'))
            dpg.set_value('c_sniper_crosshair', self.config.read_value(config_name, 'overlay','sniper_crosshair'))
            dpg.set_value('c_recoil_crosshair', self.config.read_value(config_name, 'overlay','recoil_crosshair'))
            
            dpg.set_value('c_autopistol', self.config.read_value(config_name, 'misc','auto_pistol'))
            dpg.set_value('k_autopistol', self.config.read_value(config_name, 'misc','auto_pistol_key'))
            dpg.set_value('c_bh', self.config.read_value(config_name, 'misc','bunny_hop'))
            dpg.set_value('c_strafer', self.config.read_value(config_name, 'misc','auto_strafe'))
            dpg.set_value('c_zeus', self.config.read_value(config_name, 'misc','auto_zeus'))
            dpg.set_value('c_knifebot', self.config.read_value(config_name, 'misc','knife_bot'))
            dpg.set_value('c_fps', self.config.read_value(config_name, 'misc','show_fps'))
            if self.config.read_value(config_name, 'misc','lag_strength') <= dpg.get_item_configuration('s_fakelag_str')['max_value']: dpg.set_value('s_fakelag_str',self.config.read_value(config_name, 'misc','lag_strength'))
        
    def key_handler(self, key: str):
        return h.gui_keys_list.get(dpg.get_value(key))
