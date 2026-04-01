# Procesarea Imaginilor

### Prerequisites
1. Acest proiect foloseste [**UV**](https://docs.astral.sh/uv/#highlights). Instalarea se poate face prin rularea in __PowerShell__ a urmatori comenzi: 

    ```powershell
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

### Pasi pentru rulare
1. Clonarea repositoriului

   ```
   git clone https://github.com/Madolchy/Procesarea-Imaginilor
   ```

2. Asigurate ca esti in directoriul sursa

    ```bash
    cd Procesarea-Imaginilor
    ```

3. Instalarea dependentelor
   ```bash
   uv sync
   ```
4. Rularea aplicatiei
   ``` bash
   uv run src/main.py
   ```
> [!NOTE]
> Nu este strinct necesar a folosi UV, se pot urmari si pasi clasici de `pip install`, etc...


## 3. Capturi de ecran
![ex1](/examples/clip_20260401_204538.png)
![ex2](/examples/clip_20260401_204552.png)
![ex3](/examples/clip_20260401_204614.png)