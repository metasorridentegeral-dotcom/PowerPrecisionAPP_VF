import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import DashboardLayout from "../layouts/DashboardLayout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Textarea } from "../components/ui/textarea";
import { Calendar } from "../components/ui/calendar";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { Separator } from "../components/ui/separator";
import { Popover, PopoverContent, PopoverTrigger } from "../components/ui/popover";
import {
  getProcess,
  updateProcess,
  getDeadlines,
  createDeadline,
  updateDeadline,
  deleteDeadline,
} from "../services/api";
import {
  ArrowLeft,
  User,
  Briefcase,
  Building2,
  CreditCard,
  Calendar as CalendarIcon,
  Clock,
  Plus,
  Check,
  X,
  Trash2,
  Edit,
  Loader2,
  AlertCircle,
} from "lucide-react";
import { toast } from "sonner";
import { format, parseISO, isAfter, isBefore, addDays } from "date-fns";
import { pt } from "date-fns/locale";

const statusLabels = {
  pedido_inicial: "Pedido Inicial",
  em_analise: "Em Análise",
  autorizacao_bancaria: "Autorização Bancária",
  aprovado: "Aprovado",
  rejeitado: "Rejeitado",
};

const typeLabels = {
  credito: "Crédito",
  imobiliaria: "Imobiliária",
  ambos: "Crédito + Imobiliária",
};

const ProcessDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [process, setProcess] = useState(null);
  const [deadlines, setDeadlines] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [activeTab, setActiveTab] = useState("personal");

  // Form states
  const [personalData, setPersonalData] = useState({});
  const [financialData, setFinancialData] = useState({});
  const [realEstateData, setRealEstateData] = useState({});
  const [creditData, setCreditData] = useState({});
  const [status, setStatus] = useState("");

  // Deadline dialog
  const [isDeadlineDialogOpen, setIsDeadlineDialogOpen] = useState(false);
  const [deadlineForm, setDeadlineForm] = useState({
    title: "",
    description: "",
    due_date: "",
    priority: "medium",
  });
  const [selectedDate, setSelectedDate] = useState(null);

  useEffect(() => {
    fetchData();
  }, [id]);

  const fetchData = async () => {
    try {
      const [processRes, deadlinesRes] = await Promise.all([
        getProcess(id),
        getDeadlines(id),
      ]);
      const processData = processRes.data;
      setProcess(processData);
      setDeadlines(deadlinesRes.data);
      setStatus(processData.status);
      setPersonalData(processData.personal_data || {});
      setFinancialData(processData.financial_data || {});
      setRealEstateData(processData.real_estate_data || {});
      setCreditData(processData.credit_data || {});
    } catch (error) {
      console.error("Error fetching data:", error);
      toast.error("Erro ao carregar dados do processo");
      navigate(-1);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const updateData = {};

      if (user.role === "cliente" || user.role === "admin") {
        updateData.personal_data = personalData;
        updateData.financial_data = financialData;
      }

      if (user.role === "consultor" || user.role === "admin") {
        updateData.personal_data = personalData;
        updateData.financial_data = financialData;
        updateData.real_estate_data = realEstateData;
      }

      if (user.role === "mediador" || user.role === "admin") {
        updateData.personal_data = personalData;
        updateData.financial_data = financialData;
        if (process.status === "autorizacao_bancaria" || process.status === "aprovado") {
          updateData.credit_data = creditData;
        }
      }

      if (user.role !== "cliente" && status !== process.status) {
        updateData.status = status;
      }

      await updateProcess(id, updateData);
      toast.success("Processo atualizado com sucesso!");
      fetchData();
    } catch (error) {
      console.error("Error saving process:", error);
      toast.error(error.response?.data?.detail || "Erro ao guardar processo");
    } finally {
      setSaving(false);
    }
  };

  const handleCreateDeadline = async () => {
    if (!deadlineForm.title || !selectedDate) {
      toast.error("Preencha o título e a data");
      return;
    }

    try {
      await createDeadline({
        process_id: id,
        title: deadlineForm.title,
        description: deadlineForm.description,
        due_date: format(selectedDate, "yyyy-MM-dd"),
        priority: deadlineForm.priority,
      });
      toast.success("Prazo criado com sucesso!");
      setIsDeadlineDialogOpen(false);
      setDeadlineForm({ title: "", description: "", due_date: "", priority: "medium" });
      setSelectedDate(null);
      fetchData();
    } catch (error) {
      console.error("Error creating deadline:", error);
      toast.error("Erro ao criar prazo");
    }
  };

  const handleToggleDeadline = async (deadline) => {
    try {
      await updateDeadline(deadline.id, { completed: !deadline.completed });
      fetchData();
    } catch (error) {
      console.error("Error updating deadline:", error);
      toast.error("Erro ao atualizar prazo");
    }
  };

  const handleDeleteDeadline = async (deadlineId) => {
    if (!confirm("Tem certeza que deseja eliminar este prazo?")) return;

    try {
      await deleteDeadline(deadlineId);
      toast.success("Prazo eliminado!");
      fetchData();
    } catch (error) {
      console.error("Error deleting deadline:", error);
      toast.error("Erro ao eliminar prazo");
    }
  };

  const canEditPersonal = ["cliente", "consultor", "mediador", "admin"].includes(user?.role);
  const canEditFinancial = ["cliente", "consultor", "mediador", "admin"].includes(user?.role);
  const canEditRealEstate = ["consultor", "admin"].includes(user?.role);
  const canEditCredit = ["mediador", "admin"].includes(user?.role) && 
    (process?.status === "autorizacao_bancaria" || process?.status === "aprovado");
  const canChangeStatus = ["consultor", "mediador", "admin"].includes(user?.role);
  const canManageDeadlines = ["consultor", "mediador", "admin"].includes(user?.role);

  if (loading) {
    return (
      <DashboardLayout title="Detalhes do Processo">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      </DashboardLayout>
    );
  }

  if (!process) {
    return (
      <DashboardLayout title="Processo não encontrado">
        <Card className="border-border">
          <CardContent className="p-8 text-center">
            <AlertCircle className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
            <p className="text-muted-foreground">Processo não encontrado</p>
            <Button className="mt-4" onClick={() => navigate(-1)}>
              Voltar
            </Button>
          </CardContent>
        </Card>
      </DashboardLayout>
    );
  }

  // Calendar dates with deadlines
  const deadlineDates = deadlines.map((d) => parseISO(d.due_date));

  return (
    <DashboardLayout title="Detalhes do Processo">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={() => navigate(-1)}>
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <div>
              <h2 className="text-xl font-semibold">{process.client_name}</h2>
              <p className="text-sm text-muted-foreground font-mono">
                {process.id.slice(0, 8)}... • {typeLabels[process.process_type]}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Badge className={`status-${process.status}`}>
              {statusLabels[process.status]}
            </Badge>
            {canChangeStatus && (
              <Select value={status} onValueChange={setStatus}>
                <SelectTrigger className="w-48" data-testid="status-select">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="pedido_inicial">Pedido Inicial</SelectItem>
                  <SelectItem value="em_analise">Em Análise</SelectItem>
                  <SelectItem value="autorizacao_bancaria">Autorização Bancária</SelectItem>
                  <SelectItem value="aprovado">Aprovado</SelectItem>
                  <SelectItem value="rejeitado">Rejeitado</SelectItem>
                </SelectContent>
              </Select>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            <Card className="border-border">
              <CardHeader>
                <CardTitle className="text-lg">Dados do Processo</CardTitle>
              </CardHeader>
              <CardContent>
                <Tabs value={activeTab} onValueChange={setActiveTab}>
                  <TabsList className="grid w-full grid-cols-4">
                    <TabsTrigger value="personal" className="gap-2">
                      <User className="h-4 w-4" />
                      <span className="hidden sm:inline">Pessoais</span>
                    </TabsTrigger>
                    <TabsTrigger value="financial" className="gap-2">
                      <Briefcase className="h-4 w-4" />
                      <span className="hidden sm:inline">Financeiros</span>
                    </TabsTrigger>
                    <TabsTrigger value="realestate" className="gap-2">
                      <Building2 className="h-4 w-4" />
                      <span className="hidden sm:inline">Imobiliário</span>
                    </TabsTrigger>
                    <TabsTrigger value="credit" className="gap-2">
                      <CreditCard className="h-4 w-4" />
                      <span className="hidden sm:inline">Crédito</span>
                    </TabsTrigger>
                  </TabsList>

                  {/* Personal Data Tab */}
                  <TabsContent value="personal" className="space-y-4 mt-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label>NIF</Label>
                        <Input
                          value={personalData.nif || ""}
                          onChange={(e) =>
                            setPersonalData({ ...personalData, nif: e.target.value })
                          }
                          disabled={!canEditPersonal}
                          data-testid="personal-nif"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label>Data de Nascimento</Label>
                        <Input
                          type="date"
                          value={personalData.birth_date || ""}
                          onChange={(e) =>
                            setPersonalData({ ...personalData, birth_date: e.target.value })
                          }
                          disabled={!canEditPersonal}
                          data-testid="personal-birth-date"
                        />
                      </div>
                      <div className="space-y-2 md:col-span-2">
                        <Label>Morada</Label>
                        <Input
                          value={personalData.address || ""}
                          onChange={(e) =>
                            setPersonalData({ ...personalData, address: e.target.value })
                          }
                          disabled={!canEditPersonal}
                          data-testid="personal-address"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label>Estado Civil</Label>
                        <Select
                          value={personalData.marital_status || ""}
                          onValueChange={(value) =>
                            setPersonalData({ ...personalData, marital_status: value })
                          }
                          disabled={!canEditPersonal}
                        >
                          <SelectTrigger data-testid="personal-marital-status">
                            <SelectValue placeholder="Selecione" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="solteiro">Solteiro(a)</SelectItem>
                            <SelectItem value="casado">Casado(a)</SelectItem>
                            <SelectItem value="divorciado">Divorciado(a)</SelectItem>
                            <SelectItem value="viuvo">Viúvo(a)</SelectItem>
                            <SelectItem value="uniao_facto">União de Facto</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-2">
                        <Label>Nacionalidade</Label>
                        <Input
                          value={personalData.nationality || ""}
                          onChange={(e) =>
                            setPersonalData({ ...personalData, nationality: e.target.value })
                          }
                          disabled={!canEditPersonal}
                          data-testid="personal-nationality"
                        />
                      </div>
                    </div>
                  </TabsContent>

                  {/* Financial Data Tab */}
                  <TabsContent value="financial" className="space-y-4 mt-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label>Rendimento Mensal (€)</Label>
                        <Input
                          type="number"
                          value={financialData.monthly_income || ""}
                          onChange={(e) =>
                            setFinancialData({ ...financialData, monthly_income: parseFloat(e.target.value) || null })
                          }
                          disabled={!canEditFinancial}
                          data-testid="financial-monthly-income"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label>Outros Rendimentos (€)</Label>
                        <Input
                          type="number"
                          value={financialData.other_income || ""}
                          onChange={(e) =>
                            setFinancialData({ ...financialData, other_income: parseFloat(e.target.value) || null })
                          }
                          disabled={!canEditFinancial}
                          data-testid="financial-other-income"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label>Despesas Mensais (€)</Label>
                        <Input
                          type="number"
                          value={financialData.monthly_expenses || ""}
                          onChange={(e) =>
                            setFinancialData({ ...financialData, monthly_expenses: parseFloat(e.target.value) || null })
                          }
                          disabled={!canEditFinancial}
                          data-testid="financial-monthly-expenses"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label>Tipo de Emprego</Label>
                        <Select
                          value={financialData.employment_type || ""}
                          onValueChange={(value) =>
                            setFinancialData({ ...financialData, employment_type: value })
                          }
                          disabled={!canEditFinancial}
                        >
                          <SelectTrigger data-testid="financial-employment-type">
                            <SelectValue placeholder="Selecione" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="efetivo">Contrato Efetivo</SelectItem>
                            <SelectItem value="termo">Contrato a Termo</SelectItem>
                            <SelectItem value="independente">Trabalhador Independente</SelectItem>
                            <SelectItem value="empresario">Empresário</SelectItem>
                            <SelectItem value="reformado">Reformado</SelectItem>
                            <SelectItem value="desempregado">Desempregado</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-2">
                        <Label>Entidade Empregadora</Label>
                        <Input
                          value={financialData.employer_name || ""}
                          onChange={(e) =>
                            setFinancialData({ ...financialData, employer_name: e.target.value })
                          }
                          disabled={!canEditFinancial}
                          data-testid="financial-employer-name"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label>Tempo de Emprego</Label>
                        <Input
                          value={financialData.employment_duration || ""}
                          onChange={(e) =>
                            setFinancialData({ ...financialData, employment_duration: e.target.value })
                          }
                          disabled={!canEditFinancial}
                          data-testid="financial-employment-duration"
                        />
                      </div>
                    </div>
                  </TabsContent>

                  {/* Real Estate Tab */}
                  <TabsContent value="realestate" className="space-y-4 mt-4">
                    {!canEditRealEstate && !realEstateData?.property_type ? (
                      <div className="text-center py-8 text-muted-foreground">
                        <Building2 className="h-12 w-12 mx-auto mb-4 opacity-50" />
                        <p>Dados imobiliários serão preenchidos pelo consultor</p>
                      </div>
                    ) : (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label>Tipo de Imóvel</Label>
                          <Select
                            value={realEstateData.property_type || ""}
                            onValueChange={(value) =>
                              setRealEstateData({ ...realEstateData, property_type: value })
                            }
                            disabled={!canEditRealEstate}
                          >
                            <SelectTrigger data-testid="realestate-property-type">
                              <SelectValue placeholder="Selecione" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="apartamento">Apartamento</SelectItem>
                              <SelectItem value="moradia">Moradia</SelectItem>
                              <SelectItem value="terreno">Terreno</SelectItem>
                              <SelectItem value="comercial">Espaço Comercial</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div className="space-y-2">
                          <Label>Zona Pretendida</Label>
                          <Input
                            value={realEstateData.property_zone || ""}
                            onChange={(e) =>
                              setRealEstateData({ ...realEstateData, property_zone: e.target.value })
                            }
                            disabled={!canEditRealEstate}
                            data-testid="realestate-property-zone"
                          />
                        </div>
                        <div className="space-y-2">
                          <Label>Área Pretendida (m²)</Label>
                          <Input
                            type="number"
                            value={realEstateData.desired_area || ""}
                            onChange={(e) =>
                              setRealEstateData({ ...realEstateData, desired_area: parseFloat(e.target.value) || null })
                            }
                            disabled={!canEditRealEstate}
                            data-testid="realestate-desired-area"
                          />
                        </div>
                        <div className="space-y-2">
                          <Label>Orçamento Máximo (€)</Label>
                          <Input
                            type="number"
                            value={realEstateData.max_budget || ""}
                            onChange={(e) =>
                              setRealEstateData({ ...realEstateData, max_budget: parseFloat(e.target.value) || null })
                            }
                            disabled={!canEditRealEstate}
                            data-testid="realestate-max-budget"
                          />
                        </div>
                        <div className="space-y-2">
                          <Label>Finalidade</Label>
                          <Select
                            value={realEstateData.property_purpose || ""}
                            onValueChange={(value) =>
                              setRealEstateData({ ...realEstateData, property_purpose: value })
                            }
                            disabled={!canEditRealEstate}
                          >
                            <SelectTrigger data-testid="realestate-property-purpose">
                              <SelectValue placeholder="Selecione" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="habitacao_propria">Habitação Própria</SelectItem>
                              <SelectItem value="investimento">Investimento</SelectItem>
                              <SelectItem value="arrendamento">Arrendamento</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div className="space-y-2 md:col-span-2">
                          <Label>Notas</Label>
                          <Textarea
                            value={realEstateData.notes || ""}
                            onChange={(e) =>
                              setRealEstateData({ ...realEstateData, notes: e.target.value })
                            }
                            disabled={!canEditRealEstate}
                            data-testid="realestate-notes"
                          />
                        </div>
                      </div>
                    )}
                  </TabsContent>

                  {/* Credit Tab */}
                  <TabsContent value="credit" className="space-y-4 mt-4">
                    {process.status !== "autorizacao_bancaria" && process.status !== "aprovado" ? (
                      <div className="text-center py-8 text-muted-foreground">
                        <CreditCard className="h-12 w-12 mx-auto mb-4 opacity-50" />
                        <p>Dados de crédito só podem ser preenchidos após autorização bancária</p>
                        <Badge className="mt-2 status-em_analise">
                          Estado atual: {statusLabels[process.status]}
                        </Badge>
                      </div>
                    ) : (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label>Valor do Empréstimo (€)</Label>
                          <Input
                            type="number"
                            value={creditData.requested_amount || ""}
                            onChange={(e) =>
                              setCreditData({ ...creditData, requested_amount: parseFloat(e.target.value) || null })
                            }
                            disabled={!canEditCredit}
                            data-testid="credit-requested-amount"
                          />
                        </div>
                        <div className="space-y-2">
                          <Label>Prazo (anos)</Label>
                          <Input
                            type="number"
                            value={creditData.loan_term_years || ""}
                            onChange={(e) =>
                              setCreditData({ ...creditData, loan_term_years: parseInt(e.target.value) || null })
                            }
                            disabled={!canEditCredit}
                            data-testid="credit-loan-term"
                          />
                        </div>
                        <div className="space-y-2">
                          <Label>Taxa de Juro (%)</Label>
                          <Input
                            type="number"
                            step="0.01"
                            value={creditData.interest_rate || ""}
                            onChange={(e) =>
                              setCreditData({ ...creditData, interest_rate: parseFloat(e.target.value) || null })
                            }
                            disabled={!canEditCredit}
                            data-testid="credit-interest-rate"
                          />
                        </div>
                        <div className="space-y-2">
                          <Label>Prestação Mensal (€)</Label>
                          <Input
                            type="number"
                            value={creditData.monthly_payment || ""}
                            onChange={(e) =>
                              setCreditData({ ...creditData, monthly_payment: parseFloat(e.target.value) || null })
                            }
                            disabled={!canEditCredit}
                            data-testid="credit-monthly-payment"
                          />
                        </div>
                        <div className="space-y-2">
                          <Label>Banco</Label>
                          <Input
                            value={creditData.bank_name || ""}
                            onChange={(e) =>
                              setCreditData({ ...creditData, bank_name: e.target.value })
                            }
                            disabled={!canEditCredit}
                            data-testid="credit-bank-name"
                          />
                        </div>
                        <div className="space-y-2">
                          <Label>Data de Aprovação</Label>
                          <Input
                            type="date"
                            value={creditData.bank_approval_date || ""}
                            onChange={(e) =>
                              setCreditData({ ...creditData, bank_approval_date: e.target.value })
                            }
                            disabled={!canEditCredit}
                            data-testid="credit-approval-date"
                          />
                        </div>
                        <div className="space-y-2 md:col-span-2">
                          <Label>Notas da Aprovação</Label>
                          <Textarea
                            value={creditData.bank_approval_notes || ""}
                            onChange={(e) =>
                              setCreditData({ ...creditData, bank_approval_notes: e.target.value })
                            }
                            disabled={!canEditCredit}
                            data-testid="credit-approval-notes"
                          />
                        </div>
                      </div>
                    )}
                  </TabsContent>
                </Tabs>

                <Separator className="my-6" />

                <div className="flex justify-end">
                  <Button onClick={handleSave} disabled={saving} data-testid="save-process-btn">
                    {saving ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        A guardar...
                      </>
                    ) : (
                      "Guardar Alterações"
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Sidebar - Calendar & Deadlines */}
          <div className="space-y-6">
            {/* Calendar */}
            <Card className="border-border">
              <CardHeader className="pb-2">
                <CardTitle className="text-lg flex items-center gap-2">
                  <CalendarIcon className="h-5 w-5" />
                  Calendário
                </CardTitle>
              </CardHeader>
              <CardContent>
                <Calendar
                  mode="single"
                  selected={selectedDate}
                  onSelect={setSelectedDate}
                  locale={pt}
                  modifiers={{
                    deadline: deadlineDates,
                  }}
                  modifiersStyles={{
                    deadline: {
                      backgroundColor: "hsl(var(--primary))",
                      color: "white",
                      borderRadius: "4px",
                    },
                  }}
                  className="rounded-md border"
                />
              </CardContent>
            </Card>

            {/* Deadlines */}
            <Card className="border-border">
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Clock className="h-5 w-5" />
                    Prazos
                  </CardTitle>
                  {canManageDeadlines && (
                    <Dialog open={isDeadlineDialogOpen} onOpenChange={setIsDeadlineDialogOpen}>
                      <DialogTrigger asChild>
                        <Button size="sm" variant="outline" data-testid="add-deadline-btn">
                          <Plus className="h-4 w-4" />
                        </Button>
                      </DialogTrigger>
                      <DialogContent>
                        <DialogHeader>
                          <DialogTitle>Novo Prazo</DialogTitle>
                          <DialogDescription>
                            Adicionar um novo prazo ao processo
                          </DialogDescription>
                        </DialogHeader>
                        <div className="space-y-4">
                          <div className="space-y-2">
                            <Label>Título</Label>
                            <Input
                              value={deadlineForm.title}
                              onChange={(e) =>
                                setDeadlineForm({ ...deadlineForm, title: e.target.value })
                              }
                              placeholder="Ex: Entregar documentos"
                              data-testid="deadline-title"
                            />
                          </div>
                          <div className="space-y-2">
                            <Label>Descrição</Label>
                            <Textarea
                              value={deadlineForm.description}
                              onChange={(e) =>
                                setDeadlineForm({ ...deadlineForm, description: e.target.value })
                              }
                              placeholder="Detalhes adicionais..."
                              data-testid="deadline-description"
                            />
                          </div>
                          <div className="space-y-2">
                            <Label>Data Limite</Label>
                            <Popover>
                              <PopoverTrigger asChild>
                                <Button
                                  variant="outline"
                                  className="w-full justify-start text-left font-normal"
                                  data-testid="deadline-date-btn"
                                >
                                  <CalendarIcon className="mr-2 h-4 w-4" />
                                  {selectedDate ? format(selectedDate, "PPP", { locale: pt }) : "Selecione uma data"}
                                </Button>
                              </PopoverTrigger>
                              <PopoverContent className="w-auto p-0">
                                <Calendar
                                  mode="single"
                                  selected={selectedDate}
                                  onSelect={setSelectedDate}
                                  locale={pt}
                                />
                              </PopoverContent>
                            </Popover>
                          </div>
                          <div className="space-y-2">
                            <Label>Prioridade</Label>
                            <Select
                              value={deadlineForm.priority}
                              onValueChange={(value) =>
                                setDeadlineForm({ ...deadlineForm, priority: value })
                              }
                            >
                              <SelectTrigger data-testid="deadline-priority">
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="low">Baixa</SelectItem>
                                <SelectItem value="medium">Média</SelectItem>
                                <SelectItem value="high">Alta</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>
                        </div>
                        <DialogFooter>
                          <Button onClick={handleCreateDeadline} data-testid="save-deadline-btn">
                            Criar Prazo
                          </Button>
                        </DialogFooter>
                      </DialogContent>
                    </Dialog>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                {deadlines.length === 0 ? (
                  <div className="text-center py-6 text-muted-foreground">
                    <Clock className="h-8 w-8 mx-auto mb-2 opacity-50" />
                    <p className="text-sm">Nenhum prazo definido</p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    {deadlines.map((deadline) => (
                      <div
                        key={deadline.id}
                        className={`flex items-center justify-between p-3 rounded-md ${
                          deadline.completed ? "bg-muted/30" : "bg-muted/50"
                        }`}
                        data-testid={`deadline-item-${deadline.id}`}
                      >
                        <div className="flex items-center gap-3">
                          <button
                            onClick={() => handleToggleDeadline(deadline)}
                            className={`h-5 w-5 rounded border flex items-center justify-center ${
                              deadline.completed
                                ? "bg-emerald-500 border-emerald-500 text-white"
                                : "border-slate-300"
                            }`}
                            disabled={!canManageDeadlines}
                            data-testid={`toggle-deadline-${deadline.id}`}
                          >
                            {deadline.completed && <Check className="h-3 w-3" />}
                          </button>
                          <div>
                            <p
                              className={`text-sm font-medium ${
                                deadline.completed ? "line-through text-muted-foreground" : ""
                              }`}
                            >
                              {deadline.title}
                            </p>
                            <p className="text-xs text-muted-foreground font-mono">
                              {format(parseISO(deadline.due_date), "dd/MM/yyyy")}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge className={`priority-${deadline.priority}`}>
                            {deadline.priority === "high"
                              ? "Alta"
                              : deadline.priority === "medium"
                              ? "Média"
                              : "Baixa"}
                          </Badge>
                          {canManageDeadlines && (
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-7 w-7"
                              onClick={() => handleDeleteDeadline(deadline.id)}
                              data-testid={`delete-deadline-${deadline.id}`}
                            >
                              <Trash2 className="h-4 w-4 text-destructive" />
                            </Button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default ProcessDetails;
