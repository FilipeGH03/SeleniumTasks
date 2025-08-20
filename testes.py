import consultaLattes as cl 




def lattesGetTitle(nome):
    cl.open_cnpq_homepage()
    cl.check_all_curricula()
    cl.enter_search_name(nome)
    cl.click_search_button()
    if cl.count_search_results() == 1:
        cl.click_result_by_index(0)
        cl.click_search_groups()
        return cl.get_curriculum_title()
    else:    
        cl.click_result_by_index(0)
        cl.click_search_groups()
        return cl.get_curriculum_title() + " (vários resultados)"
