# PyInstaller Build Instructions

To build the executable with the new Tkinter GUI, run the following command:

```bash
pyinstaller --name AutoCheckBJMF_GUI --onefile --noconsole --clean gui.py
```

This will generate a single executable file in the `dist` directory. Tkinter is natively supported by PyInstaller and does not require complex multiprocessing handling like Flet does.
