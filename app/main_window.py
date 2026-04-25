"""
主窗口模块
"""
import sys
import os
import webbrowser
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QComboBox, QRadioButton, QButtonGroup,
    QScrollArea, QFrame, QGroupBox, QMessageBox, QTextEdit,
    QDialog, QDialogButtonBox, QListWidget, QListWidgetItem,
    QFormLayout, QSpinBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
import config
from core.database.db_manager import DatabaseManager
from core.services.search_service import SearchService
from core.api.gaode import GaodeAPI


class SearchThread(QThread):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    
    def __init__(self, search_service, address, keyword, radius, poi_type):
        super().__init__()
        self.search_service = search_service
        self.address = address
        self.keyword = keyword
        self.radius = radius
        self.poi_type = poi_type
    
    def run(self):
        try:
            results = self.search_service.search_nearby(
                self.address, self.keyword, self.radius, self.poi_type
            )
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager(config.DB_PATH)
        self.search_service = SearchService(self.db_manager)
        self.gaode_api = GaodeAPI()
        self.current_address = None
        self.search_thread = None
        self.results = []
        self.detail_mode = False
        
        self.init_ui()
        self.load_saved_addresses()
    
    def init_ui(self):
        self.setWindowTitle(config.WINDOW_TITLE)
        self.setGeometry(100, 100, config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        self.create_address_section(main_layout)
        self.create_search_section(main_layout)
        self.create_results_section(main_layout)
        self.create_footer_buttons(main_layout)
    
    def create_address_section(self, parent_layout):
        address_group = QGroupBox("我的居住地址")
        address_layout = QHBoxLayout()
        
        address_layout.addWidget(QLabel("地址:"))
        
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("请输入居住地址，如：成都郫都区xxx小区")
        self.address_input.textChanged.connect(self.on_address_changed)
        address_layout.addWidget(self.address_input, 1)
        
        self.select_address_btn = QPushButton("选择地址")
        self.select_address_btn.clicked.connect(self.show_address_dialog)
        address_layout.addWidget(self.select_address_btn)
        
        address_group.setLayout(address_layout)
        parent_layout.addWidget(address_group)
    
    def create_search_section(self, parent_layout):
        search_group = QGroupBox("查询条件")
        search_layout = QVBoxLayout()
        
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("查询类型:"))
        
        self.query_type_group = QButtonGroup(self)
        
        self.radio_kindergarten = QRadioButton("幼儿园")
        self.radio_hospital = QRadioButton("医院")
        self.radio_mall = QRadioButton("商场")
        self.radio_school = QRadioButton("学校")
        self.radio_other = QRadioButton("其他:")
        
        self.radio_kindergarten.setChecked(True)
        
        self.query_type_group.addButton(self.radio_kindergarten)
        self.query_type_group.addButton(self.radio_hospital)
        self.query_type_group.addButton(self.radio_mall)
        self.query_type_group.addButton(self.radio_school)
        self.query_type_group.addButton(self.radio_other)
        
        type_layout.addWidget(self.radio_kindergarten)
        type_layout.addWidget(self.radio_hospital)
        type_layout.addWidget(self.radio_mall)
        type_layout.addWidget(self.radio_school)
        type_layout.addWidget(self.radio_other)
        
        self.other_keyword = QLineEdit()
        self.other_keyword.setPlaceholderText("输入关键词")
        self.other_keyword.setEnabled(False)
        type_layout.addWidget(self.other_keyword)
        type_layout.addStretch()
        
        self.radio_other.toggled.connect(self.other_keyword.setEnabled)
        
        search_layout.addLayout(type_layout)
        
        options_layout = QHBoxLayout()
        options_layout.addWidget(QLabel("搜索半径:"))
        
        self.radius_combo = QComboBox()
        for r in config.SEARCH_RADIUS_OPTIONS:
            self.radius_combo.addItem(f"{r}米", r)
        self.radius_combo.setCurrentIndex(0)
        options_layout.addWidget(self.radius_combo)
        
        options_layout.addWidget(QLabel("  显示模式:"))
        
        self.display_mode_group = QButtonGroup(self)
        self.radio_simple = QRadioButton("简洁")
        self.radio_detail = QRadioButton("详细")
        self.radio_simple.setChecked(True)
        
        self.display_mode_group.addButton(self.radio_simple)
        self.display_mode_group.addButton(self.radio_detail)
        
        options_layout.addWidget(self.radio_simple)
        options_layout.addWidget(self.radio_detail)
        options_layout.addStretch()
        
        self.detail_mode = False
        self.radio_simple.toggled.connect(lambda x: self.set_detail_mode(False))
        self.radio_detail.toggled.connect(lambda x: self.set_detail_mode(True))
        
        search_layout.addLayout(options_layout)
        
        search_btn_layout = QHBoxLayout()
        search_btn_layout.addStretch()
        
        self.search_btn = QPushButton("开始查询")
        self.search_btn.clicked.connect(self.start_search)
        self.search_btn.setMinimumWidth(120)
        self.search_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        search_btn_layout.addWidget(self.search_btn)
        
        search_layout.addLayout(search_btn_layout)
        
        search_group.setLayout(search_layout)
        parent_layout.addWidget(search_group)
    
    def set_detail_mode(self, detail: bool):
        self.detail_mode = detail
        if self.results:
            self.display_results(self.results)
    
    def create_results_section(self, parent_layout):
        results_group = QGroupBox("查询结果")
        results_layout = QVBoxLayout()
        
        self.result_count_label = QLabel("共找到 0 个结果")
        results_layout.addWidget(self.result_count_label)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMinimumHeight(300)
        
        self.results_widget = QWidget()
        self.results_layout = QVBoxLayout()
        self.results_widget.setLayout(self.results_layout)
        
        self.scroll_area.setWidget(self.results_widget)
        results_layout.addWidget(self.scroll_area)
        
        results_group.setLayout(results_layout)
        parent_layout.addWidget(results_group, 1)
    
    def create_footer_buttons(self, parent_layout):
        footer_layout = QHBoxLayout()
        
        self.btn_address_manage = QPushButton("地址管理")
        self.btn_address_manage.clicked.connect(self.show_address_dialog)
        
        self.btn_data_update = QPushButton("数据更新")
        self.btn_data_update.clicked.connect(self.show_data_update_dialog)
        
        self.btn_history = QPushButton("历史记录")
        self.btn_history.clicked.connect(self.show_history_dialog)
        
        self.btn_settings = QPushButton("设置")
        self.btn_settings.clicked.connect(self.show_settings_dialog)
        
        footer_layout.addWidget(self.btn_address_manage)
        footer_layout.addWidget(self.btn_data_update)
        footer_layout.addWidget(self.btn_history)
        footer_layout.addWidget(self.btn_settings)
        footer_layout.addStretch()
        
        parent_layout.addLayout(footer_layout)
    
    def on_address_changed(self, text):
        self.current_address = text
    
    def get_query_keyword(self):
        if self.radio_kindergarten.isChecked():
            return "幼儿园"
        elif self.radio_hospital.isChecked():
            return "医院"
        elif self.radio_mall.isChecked():
            return "商场"
        elif self.radio_school.isChecked():
            return "学校"
        elif self.radio_other.isChecked():
            return self.other_keyword.text().strip()
        return "幼儿园"
    
    def get_poi_type(self):
        if self.radio_kindergarten.isChecked():
            return "幼儿园"
        elif self.radio_hospital.isChecked():
            return "医院"
        elif self.radio_mall.isChecked():
            return "商场"
        elif self.radio_school.isChecked():
            return "学校"
        return None
    
    def start_search(self):
        address = self.address_input.text().strip()
        if not address:
            QMessageBox.warning(self, "提示", "请输入居住地址")
            return
        
        keyword = self.get_query_keyword()
        if not keyword:
            QMessageBox.warning(self, "提示", "请选择查询类型或输入关键词")
            return
        
        radius = self.radius_combo.currentData()
        poi_type = self.get_poi_type()
        
        self.search_btn.setEnabled(False)
        self.search_btn.setText("查询中...")
        self.clear_results()
        
        self.search_thread = SearchThread(
            self.search_service, address, keyword, radius, poi_type
        )
        self.search_thread.finished.connect(self.on_search_finished)
        self.search_thread.error.connect(self.on_search_error)
        self.search_thread.start()
    
    def on_search_finished(self, results):
        self.search_btn.setEnabled(True)
        self.search_btn.setText("开始查询")
        
        self.results = results
        self.result_count_label.setText(f"共找到 {len(results)} 个结果")
        
        if not results:
            QMessageBox.information(self, "提示", "未找到相关结果，请尝试调整搜索条件")
        
        self.display_results(results)
    
    def on_search_error(self, error_msg):
        self.search_btn.setEnabled(True)
        self.search_btn.setText("开始查询")
        QMessageBox.critical(self, "错误", f"查询失败: {error_msg}")
    
    def display_results(self, results):
        self.clear_results()
        
        for result in results:
            card = self.create_result_card(result)
            self.results_layout.addWidget(card)
        
        self.results_layout.addStretch()
    
    def create_result_card(self, result):
        card = QFrame()
        card.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        card.setStyleSheet("""
            QFrame {
                background-color: #f9f9f9;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                padding: 10px;
                margin: 5px 0;
            }
        """)
        
        card_layout = QVBoxLayout()
        card.setLayout(card_layout)
        
        name_label = QLabel(f"🏫 {result['name']}")
        name_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        card_layout.addWidget(name_label)
        
        address_label = QLabel(f"地址: {result['address']}")
        address_label.setStyleSheet("color: #666;")
        card_layout.addWidget(address_label)
        
        distance = result['distance']
        distance_text = f"{distance:.1f}公里" if distance >= 1 else f"{int(distance * 1000)}米"
        info_parts = [f"距离: {distance_text}"]
        
        if result.get('kindergarten') and result['kindergarten'].get('type'):
            kg_type = result['kindergarten']['type']
            info_parts.append(f"性质: {kg_type}")
        
        if result.get('lottery') and result['lottery'].get('win_rate'):
            win_rate = result['lottery']['win_rate']
            info_parts.append(f"摇号概率: {win_rate}%")
        
        info_label = QLabel("  |  ".join(info_parts))
        card_layout.addWidget(info_label)
        
        if result.get('walking') or result.get('transit'):
            transport_layout = QVBoxLayout()
            
            if result.get('transit'):
                transit = result['transit']
                line_name = transit.get('line_name', '公交/地铁')
                departure = transit.get('departure_stop', '')
                arrival = transit.get('arrival_stop', '')
                station_count = transit.get('station_count', 0)
                duration_text = transit.get('duration_text', '')
                
                if self.detail_mode:
                    transit_text = f"🚇 {line_name}: {duration_text}"
                    if departure and arrival:
                        transit_text += f"\n    上车: {departure}  |  下车: {arrival}"
                    if station_count:
                        transit_text += f"  (共{station_count}站)"
                else:
                    transit_text = f"🚇 {line_name}: {duration_text}"
                    if departure and arrival:
                        transit_text += f"  上车: {departure}  下车: {arrival}"
                    if station_count:
                        transit_text += f"({station_count}站)"
                
                transport_layout.addWidget(QLabel(transit_text))
            
            if result.get('walking'):
                walking = result['walking']
                duration_text = walking.get('duration_text', '')
                distance_text = walking.get('distance_text', '')
                transport_layout.addWidget(QLabel(f"🚶 步行: {duration_text} ({distance_text})"))
            
            card_layout.addLayout(transport_layout)
        
        if result.get('source_links'):
            links_layout = QHBoxLayout()
            links_layout.addWidget(QLabel("📎 参考数据源:"))
            
            links = result['source_links']
            
            btn_enrollment = QPushButton("招生范围")
            btn_enrollment.clicked.connect(lambda: webbrowser.open(links['enrollment']))
            links_layout.addWidget(btn_enrollment)
            
            btn_lottery = QPushButton("摇号结果")
            btn_lottery.clicked.connect(lambda: webbrowser.open(links['lottery']))
            links_layout.addWidget(btn_lottery)
            
            btn_baike = QPushButton("百度百科")
            btn_baike.clicked.connect(lambda: webbrowser.open(links['baike']))
            links_layout.addWidget(btn_baike)
            
            links_layout.addStretch()
            card_layout.addLayout(links_layout)
        
        return card
    
    def clear_results(self):
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def load_saved_addresses(self):
        addresses = self.db_manager.get_addresses()
        if addresses:
            self.current_address = addresses[0]
            self.address_input.setText(addresses[0]['address'])
    
    def show_address_dialog(self):
        dialog = AddressDialog(self.db_manager, self)
        dialog.exec_()
        self.load_saved_addresses()
    
    def show_data_update_dialog(self):
        QMessageBox.information(self, "数据更新", "数据更新功能开发中...")
    
    def show_history_dialog(self):
        dialog = HistoryDialog(self.db_manager, self)
        dialog.exec_()
    
    def show_settings_dialog(self):
        QMessageBox.information(self, "设置", "设置功能开发中...")


class AddressDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("地址管理")
        self.setMinimumWidth(500)
        self.init_ui()
        self.load_addresses()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        self.address_list = QListWidget()
        self.address_list.setMinimumHeight(200)
        layout.addWidget(self.address_list)
        
        btn_layout = QHBoxLayout()
        
        self.btn_add = QPushButton("新增")
        self.btn_add.clicked.connect(self.add_address)
        btn_layout.addWidget(self.btn_add)
        
        self.btn_edit = QPushButton("编辑")
        self.btn_edit.clicked.connect(self.edit_address)
        btn_layout.addWidget(self.btn_edit)
        
        self.btn_delete = QPushButton("删除")
        self.btn_delete.clicked.connect(self.delete_address)
        btn_layout.addWidget(self.btn_delete)
        
        btn_layout.addStretch()
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)
        btn_layout.addWidget(buttons)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def load_addresses(self):
        self.address_list.clear()
        addresses = self.db_manager.get_addresses()
        for addr in addresses:
            item = QListWidgetItem(f"{addr['name']} - {addr['address']}")
            item.setData(Qt.UserRole, addr)
            self.address_list.addItem(item)
    
    def add_address(self):
        dialog = AddressEditDialog(self.db_manager, self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_addresses()
    
    def edit_address(self):
        item = self.address_list.currentItem()
        if not item:
            QMessageBox.warning(self, "提示", "请选择要编辑的地址")
            return
        address = item.data(Qt.UserRole)
        dialog = AddressEditDialog(self.db_manager, self, address)
        if dialog.exec_() == QDialog.Accepted:
            self.load_addresses()
    
    def delete_address(self):
        item = self.address_list.currentItem()
        if not item:
            QMessageBox.warning(self, "提示", "请选择要删除的地址")
            return
        address = item.data(Qt.UserRole)
        reply = QMessageBox.question(self, "确认", "确定要删除该地址吗?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db_manager.delete_address(address['id'])
            self.load_addresses()


class AddressEditDialog(QDialog):
    def __init__(self, db_manager, parent=None, address=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.address = address
        self.setWindowTitle("编辑地址" if address else "新增地址")
        self.setMinimumWidth(400)
        self.init_ui()
    
    def init_ui(self):
        layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("如：家、公司")
        layout.addRow("名称:", self.name_input)
        
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("完整地址")
        layout.addRow("地址:", self.address_input)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        self.setLayout(layout)
        
        if self.address:
            self.name_input.setText(self.address['name'])
            self.address_input.setText(self.address['address'])
    
    def save(self):
        name = self.name_input.text().strip()
        address = self.address_input.text().strip()
        
        if not name or not address:
            QMessageBox.warning(self, "提示", "请填写完整信息")
            return
        
        gaode_api = GaodeAPI()
        geocode_result = gaode_api.geocode(address)
        
        if not geocode_result:
            QMessageBox.warning(self, "提示", "无法解析地址，请检查地址是否正确")
            return
        
        if self.address:
            self.db_manager.update_address(
                self.address['id'], name, address,
                geocode_result['lat'], geocode_result['lng']
            )
        else:
            self.db_manager.add_address(
                name, address,
                geocode_result['lat'], geocode_result['lng']
            )
        
        self.accept()


class HistoryDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("搜索历史")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        self.init_ui()
        self.load_history()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        self.history_list = QListWidget()
        layout.addWidget(self.history_list)
        
        btn_layout = QHBoxLayout()
        
        self.btn_clear = QPushButton("清空历史")
        self.btn_clear.clicked.connect(self.clear_history)
        btn_layout.addWidget(self.btn_clear)
        
        btn_layout.addStretch()
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)
        btn_layout.addWidget(buttons)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def load_history(self):
        self.history_list.clear()
        history = self.db_manager.get_search_history()
        for item in history:
            text = f"{item['searched_at']} - {item['address_name']}: {item['keyword']}"
            self.history_list.addItem(text)
    
    def clear_history(self):
        reply = QMessageBox.question(self, "确认", "确定要清空所有历史记录吗?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db_manager.clear_history()
            self.load_history()