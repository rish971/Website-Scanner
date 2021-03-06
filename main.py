import logging
import threading
import tkinter as tk
from tkinter import messagebox, filedialog, ttk

import url_func
from crawler_files import CrawlerFiles
from website_scanner import WebsiteScanner

# create logger
logger = logging.getLogger()

min_nc = 1
max_nc = 10
min_cs = 1024
max_cs = 102400
min_ct = 5.0
min_dd = 0.0
max_ct = max_dd = 30.0


class MainMenu(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        # logger
        MainMenu.init_logger()
        # variables
        self.title('Main Menu')
        logger.info('Initiating Start Menu')
        self.save_dir = tk.StringVar()
        self.start_url = tk.StringVar()
        self.entry_str = tk.StringVar()
        self.chunk_size = tk.StringVar()
        self.conn_timeout = tk.StringVar()
        self.default_delay = tk.StringVar()
        self.usr_agent = tk.StringVar()
        self.num_crawlers = tk.StringVar()
        self.find_string_set = set()
        self.find_flname_set = set()
        self.valid_project = False
        self.cFiles = CrawlerFiles()
        self.total_time = 0
        self.download = tk.IntVar()
        #  configuring rows and cols of window to change size if window size is changed
        self.rowconfigure(4, weight=1)
        self.columnconfigure(0, weight=1)
        # Frames
        sd_frame = tk.Frame(self)  # save_dir_frame
        le_frame = tk.Frame(self)  # label_entry frame
        lb_frame = tk.Frame(self)  # listbox_frame
        sb_frame = tk.Frame(self)  # spinbox_frame
        # Frame configurations
        sd_frame.columnconfigure(1, weight=1)
        le_frame.columnconfigure(1, weight=1)
        lb_frame.rowconfigure(1, weight=1)
        for i in range(5):
            if i != 2:
                lb_frame.columnconfigure(i, weight=1)
        for i in range(11):
            if i != 2 and i != 5 and i != 8:
                sb_frame.columnconfigure(i, weight=1)
        lbl_font = ("Verdana", 11)
        ent_font = ("Cambria", 12)
        btn_font = ("Helvetica", 11)
        lbx_font = ("Segoe UI", 11)
        sbx_font = ("Cambria", 11)
        style = ttk.Style()
        style.configure('TButton', font=btn_font)
        # Labels
        tk.Label(sd_frame, text="Save Directory", font=lbl_font).grid(row=0, column=0, sticky='ew')
        tk.Label(le_frame, text="Starting URL  ", font=lbl_font).grid(row=0, column=0, sticky='ew')
        tk.Label(le_frame, text="User Agent    ", font=lbl_font).grid(row=2, column=0, sticky='ew')
        tk.Label(le_frame, text="Entry Box     ", font=lbl_font).grid(row=4, column=0, sticky='ew')
        tk.Label(sb_frame, text="  Chunk Size  ", font=lbl_font).grid(row=0, column=0, sticky='ew', padx=5)
        tk.Label(sb_frame, text="Conn. Timeout ", font=lbl_font).grid(row=0, column=3, sticky='ew', padx=5)
        tk.Label(sb_frame, text="Default Delay ", font=lbl_font).grid(row=0, column=6, sticky='ew', padx=5)
        tk.Label(sb_frame, text="Num of Crawler", font=lbl_font).grid(row=0, column=9, sticky='ew', padx=5)
        # Entries
        tk.Entry(sd_frame, textvariable=self.save_dir, font=ent_font, state='readonly').grid(row=0, column=1,
                                                                                             sticky='nsew')
        tk.Entry(le_frame, textvariable=self.start_url, font=ent_font).grid(row=0, column=1, sticky='nsew', padx=5)
        tk.Entry(le_frame, textvariable=self.usr_agent, font=ent_font).grid(row=2, column=1, sticky='nsew', padx=5)
        tk.Entry(le_frame, textvariable=self.entry_str, font=ent_font).grid(row=4, column=1, sticky='nsew', padx=5)
        # Buttons
        ttk.Button(sd_frame, text="Browse", command=self.browse).grid(row=0, column=2, padx=5)
        ttk.Button(lb_frame, text="Add String", command=lambda: self.add_to_listbox(1)).grid(row=0, column=0)
        ttk.Button(lb_frame, text="Del String", command=lambda: self.del_fm_listbox(1)).grid(row=0, column=1)
        ttk.Button(lb_frame, text=" Add File ", command=lambda: self.add_to_listbox(2)).grid(row=0, column=3)
        ttk.Button(lb_frame, text=" Del File ", command=lambda: self.del_fm_listbox(2)).grid(row=0, column=4)
        ttk.Button(self, text="Start", command=self.started).grid(row=8, column=0, sticky='ew')
        # Listbox
        self.string_lb = tk.Listbox(lb_frame, selectmode='extended', font=lbx_font)
        self.flname_lb = tk.Listbox(lb_frame, selectmode='extended', font=lbx_font)
        self.string_lb.grid(row=1, column=0, sticky='nsew', columnspan=2, rowspan=2)
        self.flname_lb.grid(row=1, column=3, sticky='nsew', columnspan=2)
        # CheckButton
        cb = tk.Checkbutton(lb_frame, text="Download Found Files?", font=lbl_font, command=self.download_file,
                            variable=self.download)
        cb.grid(row=2, column=3, columnspan=2)
        # Spinbox
        self.chunk_size_sb = tk.Spinbox(sb_frame, from_=min_cs, to=max_cs, increment=1024, wrap=True, width=8,
                                        font=sbx_font, textvariable=self.chunk_size, state='disable')
        self.chunk_size_sb.grid(row=0, column=1, sticky='nsew', padx=5)
        tk.Spinbox(sb_frame, from_=min_ct, to=max_ct, increment=1.00, wrap=True, width=8,
                   font=sbx_font, textvariable=self.conn_timeout).grid(row=0, column=4, sticky='nsew', padx=5)
        tk.Spinbox(sb_frame, from_=min_dd, to=max_dd, increment=1.00, wrap=True, width=8,
                   font=sbx_font, textvariable=self.default_delay).grid(row=0, column=7, sticky='nsew', padx=5)
        tk.Spinbox(sb_frame, from_=min_nc, to=max_nc, increment=1.00, wrap=True, width=8,
                   font=sbx_font, textvariable=self.num_crawlers).grid(row=0, column=10, sticky='nsew', padx=5)
        # Frame pack
        sd_frame.grid(row=0, column=0, sticky='ew')
        le_frame.grid(row=2, column=0, sticky='ew')
        lb_frame.grid(row=4, column=0, sticky='nsew')
        sb_frame.grid(row=6, column=0, sticky='ew')
        # Separators
        ttk.Separator(self, orient='horizontal').grid(row=1, column=0, sticky='ew')
        ttk.Separator(self, orient='horizontal').grid(row=3, column=0, sticky='ew')
        ttk.Separator(self, orient='horizontal').grid(row=5, column=0, sticky='ew')
        ttk.Separator(self, orient='horizontal').grid(row=7, column=0, sticky='ew')
        ttk.Separator(le_frame, orient='horizontal').grid(row=1, column=0, sticky='ew', columnspan=2)
        ttk.Separator(le_frame, orient='horizontal').grid(row=3, column=0, sticky='ew', columnspan=2)
        ttk.Separator(lb_frame, orient='vertical').grid(row=0, column=2, rowspan=2, stick='ns')
        ttk.Separator(sb_frame, orient='vertical').grid(row=0, column=2, stick='ns')
        ttk.Separator(sb_frame, orient='vertical').grid(row=0, column=5, stick='ns')
        ttk.Separator(sb_frame, orient='vertical').grid(row=0, column=8, stick='ns')
        # start button
        logger.info('Initialised Start Menu')

    @staticmethod
    def init_logger():
        logger.setLevel(logging.DEBUG)
        # create formatter
        formatter = logging.Formatter('%(asctime)s : %(levelname)-7s : [%(filename)s:%(lineno)d] : %(message)s')
        # create console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        # performance optimization
        # logger._srcfile = None
        # logger.logThreads = 0
        # logger.logProcesses = 0

    def browse(self):
        logger.info('Selecting Save Directory')
        # Deleting contents of entries and listbox
        self.save_dir.set('')
        self.start_url.set('')
        self.string_lb.delete(0, 'end')
        self.flname_lb.delete(0, 'end')
        self.usr_agent.set('')
        self.find_string_set.clear()
        self.find_flname_set.clear()
        self.total_time = 0
        # directory selection
        init_dir = "."
        dir_name = filedialog.askdirectory(parent=self, initialdir=init_dir, title='Please select a directory')
        if dir_name != '':
            # Setting Save Directory
            self.save_dir.set(dir_name)
            self.cFiles = CrawlerFiles(dir_name)
            # Loading Save Directory
            self.load_project()

    def started(self):
        logger.info("Starting...")
        # Checking Project Details Given
        if self.check_project():
            try:
                threading.Thread(target=self.start_handler, daemon=True).start()
            except Exception as e:
                logger.exception('Error in start_menu')
                messagebox.showerror('Error', e)
                self.cFiles.stopped()

    def start_handler(self):
        try:
            self.withdraw()
            self.cFiles.started()
            par = (self.save_dir.get(), self.start_url.get(), self.find_flname_set, self.find_string_set,
                   int(self.chunk_size.get()), float(self.conn_timeout.get()), float(self.default_delay.get()),
                   self.usr_agent.get())
            ch = WebsiteScanner(int(self.num_crawlers.get()), self.total_time)
            ch.init_logger(self.cFiles.paths[self.cFiles.log_file])
            self.total_time = ch.start_crawl(*par)
            self.cFiles.stopped()
            self.update_project()
            logger.info('Opening Save Directory')
            self.cFiles.open_save_dir()
            self.deiconify()
        except Exception as e:
            logger.exception(e)
            messagebox.showerror('Error', e)

    def load_project(self):
        try:
            config_file_list = self.cFiles.get_file_data(self.cFiles.config_file)
            if config_file_list is None:
                # nothing to load
                return
            idx = 0
            url = config_file_list[idx]  # 0
            if url_func.check_url_syntax(url):
                self.start_url.set(url)
            else:
                logger.error('Invalid start url in config file')
                messagebox.showerror('Error', 'Invalid start url in config file')
                return
            idx += 1
            num_of_string = config_file_list[idx]  # 2+nt
            idx += 1
            for _ in range(num_of_string):
                string = config_file_list[idx]  # 2+nt+1, ... ,2+nt+ns-1
                self.find_string_set.add(string)
                self.string_lb.insert('end', string)
                idx += 1
            num_of_flname = config_file_list[idx]  # 2+nt+ns
            idx += 1
            for _ in range(num_of_flname):
                flname = config_file_list[idx]  # 2+nt+ns+1, ... ,2+nt+ns+nf-1
                self.find_flname_set.add(flname)
                self.flname_lb.insert('end', flname)
                idx += 1
            self.download_file(config_file_list[idx])  # 2+nt+nf+ns
            idx += 1
            self.chunk_size.set(config_file_list[idx])
            idx += 1
            self.conn_timeout.set(config_file_list[idx])
            idx += 1
            self.default_delay.set(config_file_list[idx])
            idx += 1
            self.num_crawlers.set(config_file_list[idx])  # 2+nt+nf+ns+1
            idx += 1
            self.usr_agent.set(config_file_list[idx])
            idx += 1
            self.total_time = config_file_list[idx]
            logger.info('Done Loading data from Save Directory')
        except Exception as e:
            logger.exception('Error in loading config file - ' + e)
            messagebox.showerror('Error', e)

    def check_project(self):
        try:
            curr_url = self.start_url.get()
            logger.info('Checking start url ')
            if not self.save_dir.get():
                logger.warning('->Invalid save directory')
                messagebox.showwarning('Warning', 'Invalid save directory')
                return False
            if not url_func.check_url_syntax(curr_url):
                logger.warning('->Url Syntax Invalid')
                messagebox.showwarning('Warning', 'Invalid url syntax')
                return False
            if not check_var(float, self.conn_timeout.get(), min_val=min_ct, max_val=max_dd):
                logger.warning('->Connection Timeout must be positive float')
                messagebox.showwarning('Warning', 'Connection Timeout must be a positive float')
                return False
            if not check_var(int, self.chunk_size.get(), min_val=min_cs, max_val=max_cs):
                logger.warning('->Chunk size must be positive integer')
                messagebox.showwarning('Warning', 'Chunk size must be a positive integer')
                return False
            if not check_var(float, self.default_delay.get(), min_val=min_dd, max_val=max_dd):
                logger.warning('->Default delay must be positive float ')
                messagebox.showwarning('Warning', 'Default delay must be a positive float')
                return False
            if not check_var(int, self.num_crawlers.get(), min_val=min_nc, max_val=max_nc):
                logger.warning('->Number of Crawlers must be between ' + str(min_nc) + ' & ' + str(max_nc))
                messagebox.showwarning('Warning', 'No. of Crawlers must be b/w ' + str(min_nc) + ' & ' + str(max_nc))
                return False
            logger.info('Checking if project already running')
            if self.cFiles.is_running():
                logger.warning('->Project Running')
                messagebox.showwarning('Warning', 'Project Already Running')
                return False

            logger.info('Checking config file ')
            config_file_list = self.cFiles.get_file_data(self.cFiles.config_file)
            if config_file_list is None:
                self.cFiles.create_files(curr_url)
            else:
                url = config_file_list[0]
                if url != curr_url:
                    logger.warning('Different project found in save directory')
                    r = messagebox.askquestion('Alert', 'Another Project ' + url + ' in this directory. Load it?')
                    if r == 'yes':
                        self.start_url.set(url)
                        logger.info(url, 'set as start url')
                    elif messagebox.askquestion('Alert', 'Change ' + url + ' to ' + curr_url) == 'yes':
                        self.cFiles.change_start_url(curr_url)
                        self.total_time = 0
                    else:
                        return False
            return True
        except Exception as e:
            logger.exception('Error in check project ')
            messagebox.showerror('Error', e)
            return False

    def update_project(self):
        logger.info('Updating config file')
        config_file_list = [self.start_url.get(), len(self.find_string_set)]
        for string in self.find_string_set:
            config_file_list.append(string)
        config_file_list.append(len(self.find_flname_set))
        for flname in self.find_flname_set:
            config_file_list.append(flname)
        config_file_list.append(self.download.get())
        config_file_list.append(self.chunk_size.get())
        config_file_list.append(self.conn_timeout.get())
        config_file_list.append(self.default_delay.get())
        config_file_list.append(self.num_crawlers.get())
        config_file_list.append(self.usr_agent.get())
        config_file_list.append(self.total_time)
        self.cFiles.set_file_data(self.cFiles.config_file, config_file_list)

    def add_to_listbox(self, choice):
        string = self.entry_str.get()
        if string:
            self.entry_str.set('')
            if choice == 1:
                if string not in self.find_string_set:
                    self.find_string_set.add(string)
                    self.string_lb.insert('end', string)
                    logger.info('Added %s in find string set' % string)
            elif choice == 2:
                if string not in self.find_flname_set:
                    self.find_flname_set.add(string)
                    self.flname_lb.insert('end', string)
                    logger.info('Added %s in find file set' % string)

    def del_fm_listbox(self, choice):
        if choice == 1:
            # logger.info(self.string_lb.curselection())
            for index in self.string_lb.curselection()[::-1]:
                string = self.string_lb.get(index)
                self.find_string_set.remove(string)
                self.string_lb.delete(index)
                logger.info('Deleted %s from find string set' % string)
            self.string_lb.selection_clear(0, 'end')
        elif choice == 2:
            # logger.info(self.flname_lb.curselection())
            for index in self.flname_lb.curselection()[::-1]:
                string = self.flname_lb.get(index)
                self.find_flname_set.remove(string)
                self.flname_lb.delete(index)
                logger.info('Deleted %s from find string set' % string)
            self.flname_lb.selection_clear(0, 'end')

    def download_file(self, var=None):
        if var:
            self.download.set(var)
        logger.info('Download ' + str(self.download.get()))
        if self.download.get():
            self.chunk_size_sb.config(state='normal')
        else:
            self.chunk_size_sb.config(state='disable')


def check_var(type, value, min_val=None, max_val=None):
    rv = True
    # noinspection PyBroadException
    try:
        v = type(value)
        if min_val and v < min_val:
            rv = False
        if max_val and v > max_val:
            rv = False
    except:
        rv = False
    return rv


if __name__ == "__main__":
    sm = MainMenu()
    sm.update()
    sm.wm_minsize(sm.winfo_width(), sm.winfo_height())
    # sm.resizable(0, 0)
    sm.mainloop()
