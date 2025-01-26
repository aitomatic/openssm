@echo off


:: TARGETS
:: =======
SET TARGET=%1

IF "%TARGET%"=="streamlit-run" GOTO streamlit-run


:: STREAMLIT APP
:: =============
:streamlit-run
  poetry run streamlit run streamlit-main.py --server.allowRunOnSave=true --server.runOnSave=true
  GOTO end


:: END
:: ===
:end
