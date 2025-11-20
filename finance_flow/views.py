from django.views.generic import TemplateView
# Create your views here.


class FinanceFlowView(TemplateView):
    template_name = "finance_flow/finance-flow-control.html"