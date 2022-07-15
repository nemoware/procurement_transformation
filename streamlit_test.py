from multi_pages_wrapper import MultiApp
from streamlit_pages import create_proposal, compare_proposal

app = MultiApp()
app.add_app('Формирование предзаполненного КП', create_proposal.run)
app.add_app('Сравнение измененного инициатором КП ', compare_proposal.run)

app.run()
