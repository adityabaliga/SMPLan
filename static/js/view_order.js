function create_tables(order_detail_lst, incoming){
    var i, html, new_html, stage_no, operation, ip_size;

    for (i=0;i<order_detail_lst.length;i++){
        stage_no = order_detail_lst[i].stage_no;
        operation = order_detail_lst[i].operation;
        ip_size = order_detail_lst[i].mc_width + " x " + order_detail_lst[i].mc_length;

    }
    html = '<h2>%operation% Programme</h2><table class="table table-bordered"><th><tr>Input Size</tr><tr>Customer</tr><tr>Proc wt. (in MT)></th><td><tr>%input_size%</tr><tr>%customer%</tr><tr>%proc_wt%</tr></td></table>';
    new_html = html.replace('%operation%', operation);
    new_html = html.replace('%input_size%', ip_size);
    new_html = html.replace('%customer%', incoming.customer);

    document.getElementById('html_body').insertAdjacentHTML('beforeend', newHTML);
}