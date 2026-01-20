import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Textarea } from "../components/ui/textarea";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";
import { RadioGroup, RadioGroupItem } from "../components/ui/radio-group";
import { Checkbox } from "../components/ui/checkbox";
import { Building2, CreditCard, FileText, Loader2, ArrowLeft, ArrowRight, Check, User, Briefcase } from "lucide-react";
import { toast } from "sonner";
import axios from "axios";

const API_URL = process.env.REACT_APP_BACKEND_URL + "/api";

const PublicClientForm = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  
  const [formData, setFormData] = useState({
    // Dados básicos
    name: "",
    email: "",
    phone: "",
    // Tipo de processo
    process_type: "",
    // Dados pessoais
    nif: "",
    address: "",
    birth_date: "",
    marital_status: "",
    nationality: "Portuguesa",
    // Dados financeiros
    monthly_income: "",
    other_income: "",
    monthly_expenses: "",
    employment_type: "",
    employer_name: "",
    employment_duration: "",
    has_debts: false,
    debt_amount: "",
    // Consentimento
    consent_data: false,
    consent_contact: false,
  });

  const handleSubmit = async () => {
    if (!formData.consent_data || !formData.consent_contact) {
      toast.error("Por favor, aceite os termos para continuar");
      return;
    }

    setLoading(true);

    try {
      await axios.post(`${API_URL}/public/client-registration`, {
        name: formData.name,
        email: formData.email,
        phone: formData.phone,
        process_type: formData.process_type,
        personal_data: {
          nif: formData.nif,
          address: formData.address,
          birth_date: formData.birth_date,
          marital_status: formData.marital_status,
          nationality: formData.nationality,
        },
        financial_data: {
          monthly_income: formData.monthly_income ? parseFloat(formData.monthly_income) : null,
          other_income: formData.other_income ? parseFloat(formData.other_income) : null,
          monthly_expenses: formData.monthly_expenses ? parseFloat(formData.monthly_expenses) : null,
          employment_type: formData.employment_type,
          employer_name: formData.employer_name,
          employment_duration: formData.employment_duration,
          has_debts: formData.has_debts,
          debt_amount: formData.debt_amount ? parseFloat(formData.debt_amount) : null,
        },
      });

      setSubmitted(true);
      toast.success("Registo enviado com sucesso!");
    } catch (error) {
      console.error("Error submitting form:", error);
      toast.error(error.response?.data?.detail || "Erro ao enviar registo");
    } finally {
      setLoading(false);
    }
  };

  const renderStepIndicator = () => (
    <div className="flex items-center justify-center mb-8">
      {[1, 2, 3, 4].map((s) => (
        <div key={s} className="flex items-center">
          <div
            className={`h-10 w-10 rounded-full flex items-center justify-center text-sm font-semibold transition-all ${
              s < step
                ? "bg-emerald-500 text-white"
                : s === step
                ? "bg-primary text-primary-foreground"
                : "bg-muted text-muted-foreground"
            }`}
          >
            {s < step ? <Check className="h-5 w-5" /> : s}
          </div>
          {s < 4 && (
            <div className={`h-1 w-12 mx-2 transition-all ${s < step ? "bg-emerald-500" : "bg-muted"}`} />
          )}
        </div>
      ))}
    </div>
  );

  const renderStep1 = () => (
    <div className="space-y-6">
      <div className="text-center mb-6">
        <h2 className="text-xl font-semibold mb-2">Tipo de Serviço</h2>
        <p className="text-muted-foreground">Selecione o tipo de ajuda que precisa</p>
      </div>
      <RadioGroup
        value={formData.process_type}
        onValueChange={(value) => setFormData({ ...formData, process_type: value })}
        className="grid grid-cols-1 md:grid-cols-3 gap-4"
      >
        <div>
          <RadioGroupItem value="credito" id="credito" className="peer sr-only" />
          <Label
            htmlFor="credito"
            className="flex flex-col items-center justify-center p-6 border-2 rounded-lg cursor-pointer transition-all peer-data-[state=checked]:border-primary peer-data-[state=checked]:bg-primary/5 hover:bg-muted/50"
            data-testid="process-type-credito"
          >
            <CreditCard className="h-10 w-10 mb-3 text-primary" />
            <span className="font-semibold">Crédito</span>
            <span className="text-sm text-muted-foreground text-center mt-1">
              Crédito habitação ou pessoal
            </span>
          </Label>
        </div>
        <div>
          <RadioGroupItem value="imobiliaria" id="imobiliaria" className="peer sr-only" />
          <Label
            htmlFor="imobiliaria"
            className="flex flex-col items-center justify-center p-6 border-2 rounded-lg cursor-pointer transition-all peer-data-[state=checked]:border-primary peer-data-[state=checked]:bg-primary/5 hover:bg-muted/50"
            data-testid="process-type-imobiliaria"
          >
            <Building2 className="h-10 w-10 mb-3 text-primary" />
            <span className="font-semibold">Imobiliária</span>
            <span className="text-sm text-muted-foreground text-center mt-1">
              Procura de imóvel
            </span>
          </Label>
        </div>
        <div>
          <RadioGroupItem value="ambos" id="ambos" className="peer sr-only" />
          <Label
            htmlFor="ambos"
            className="flex flex-col items-center justify-center p-6 border-2 rounded-lg cursor-pointer transition-all peer-data-[state=checked]:border-primary peer-data-[state=checked]:bg-primary/5 hover:bg-muted/50"
            data-testid="process-type-ambos"
          >
            <FileText className="h-10 w-10 mb-3 text-primary" />
            <span className="font-semibold">Ambos</span>
            <span className="text-sm text-muted-foreground text-center mt-1">
              Crédito + Imobiliária
            </span>
          </Label>
        </div>
      </RadioGroup>
    </div>
  );

  const renderStep2 = () => (
    <div className="space-y-6">
      <div className="text-center mb-6">
        <User className="h-10 w-10 mx-auto mb-2 text-primary" />
        <h2 className="text-xl font-semibold mb-2">Dados Pessoais</h2>
        <p className="text-muted-foreground">Preencha os seus dados de contacto e identificação</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2 md:col-span-2">
          <Label htmlFor="name">Nome Completo *</Label>
          <Input
            id="name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="O seu nome completo"
            required
            data-testid="client-name"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="email">Email *</Label>
          <Input
            id="email"
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            placeholder="seu@email.com"
            required
            data-testid="client-email"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="phone">Telefone *</Label>
          <Input
            id="phone"
            value={formData.phone}
            onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
            placeholder="+351 912 345 678"
            required
            data-testid="client-phone"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="nif">NIF *</Label>
          <Input
            id="nif"
            value={formData.nif}
            onChange={(e) => setFormData({ ...formData, nif: e.target.value })}
            placeholder="123456789"
            required
            data-testid="client-nif"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="birth_date">Data de Nascimento</Label>
          <Input
            id="birth_date"
            type="date"
            value={formData.birth_date}
            onChange={(e) => setFormData({ ...formData, birth_date: e.target.value })}
            data-testid="client-birth-date"
          />
        </div>
        <div className="space-y-2 md:col-span-2">
          <Label htmlFor="address">Morada</Label>
          <Input
            id="address"
            value={formData.address}
            onChange={(e) => setFormData({ ...formData, address: e.target.value })}
            placeholder="Rua, número, código postal, cidade"
            data-testid="client-address"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="marital_status">Estado Civil</Label>
          <Select
            value={formData.marital_status}
            onValueChange={(value) => setFormData({ ...formData, marital_status: value })}
          >
            <SelectTrigger data-testid="client-marital-status">
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
          <Label htmlFor="nationality">Nacionalidade</Label>
          <Input
            id="nationality"
            value={formData.nationality}
            onChange={(e) => setFormData({ ...formData, nationality: e.target.value })}
            placeholder="Portuguesa"
            data-testid="client-nationality"
          />
        </div>
      </div>
    </div>
  );

  const renderStep3 = () => (
    <div className="space-y-6">
      <div className="text-center mb-6">
        <Briefcase className="h-10 w-10 mx-auto mb-2 text-primary" />
        <h2 className="text-xl font-semibold mb-2">Dados Financeiros</h2>
        <p className="text-muted-foreground">Informações sobre a sua situação financeira</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="monthly_income">Rendimento Mensal Líquido (€) *</Label>
          <Input
            id="monthly_income"
            type="number"
            value={formData.monthly_income}
            onChange={(e) => setFormData({ ...formData, monthly_income: e.target.value })}
            placeholder="0.00"
            required
            data-testid="client-monthly-income"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="other_income">Outros Rendimentos (€)</Label>
          <Input
            id="other_income"
            type="number"
            value={formData.other_income}
            onChange={(e) => setFormData({ ...formData, other_income: e.target.value })}
            placeholder="0.00"
            data-testid="client-other-income"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="monthly_expenses">Despesas Mensais (€)</Label>
          <Input
            id="monthly_expenses"
            type="number"
            value={formData.monthly_expenses}
            onChange={(e) => setFormData({ ...formData, monthly_expenses: e.target.value })}
            placeholder="0.00"
            data-testid="client-monthly-expenses"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="employment_type">Situação Profissional *</Label>
          <Select
            value={formData.employment_type}
            onValueChange={(value) => setFormData({ ...formData, employment_type: value })}
          >
            <SelectTrigger data-testid="client-employment-type">
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
          <Label htmlFor="employer_name">Entidade Empregadora</Label>
          <Input
            id="employer_name"
            value={formData.employer_name}
            onChange={(e) => setFormData({ ...formData, employer_name: e.target.value })}
            placeholder="Nome da empresa"
            data-testid="client-employer-name"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="employment_duration">Tempo na Empresa</Label>
          <Input
            id="employment_duration"
            value={formData.employment_duration}
            onChange={(e) => setFormData({ ...formData, employment_duration: e.target.value })}
            placeholder="Ex: 2 anos"
            data-testid="client-employment-duration"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="has_debts">Tem encargos financeiros?</Label>
          <Select
            value={formData.has_debts ? "yes" : "no"}
            onValueChange={(value) => setFormData({ ...formData, has_debts: value === "yes" })}
          >
            <SelectTrigger data-testid="client-has-debts">
              <SelectValue placeholder="Selecione" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="no">Não</SelectItem>
              <SelectItem value="yes">Sim</SelectItem>
            </SelectContent>
          </Select>
        </div>
        {formData.has_debts && (
          <div className="space-y-2">
            <Label htmlFor="debt_amount">Valor Mensal dos Encargos (€)</Label>
            <Input
              id="debt_amount"
              type="number"
              value={formData.debt_amount}
              onChange={(e) => setFormData({ ...formData, debt_amount: e.target.value })}
              placeholder="0.00"
              data-testid="client-debt-amount"
            />
          </div>
        )}
      </div>
    </div>
  );

  const renderStep4 = () => (
    <div className="space-y-6">
      <div className="text-center mb-6">
        <Check className="h-10 w-10 mx-auto mb-2 text-primary" />
        <h2 className="text-xl font-semibold mb-2">Confirmação</h2>
        <p className="text-muted-foreground">Reveja os seus dados e confirme o registo</p>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="border-border">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Dados Pessoais</CardTitle>
          </CardHeader>
          <CardContent className="space-y-1 text-sm">
            <p><strong>Nome:</strong> {formData.name}</p>
            <p><strong>Email:</strong> {formData.email}</p>
            <p><strong>Telefone:</strong> {formData.phone}</p>
            <p><strong>NIF:</strong> {formData.nif}</p>
          </CardContent>
        </Card>
        <Card className="border-border">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Dados Financeiros</CardTitle>
          </CardHeader>
          <CardContent className="space-y-1 text-sm">
            <p><strong>Rendimento:</strong> {formData.monthly_income ? `€${formData.monthly_income}` : "-"}</p>
            <p><strong>Situação:</strong> {formData.employment_type || "-"}</p>
            <p><strong>Empregador:</strong> {formData.employer_name || "-"}</p>
          </CardContent>
        </Card>
      </div>

      {/* Consent checkboxes */}
      <div className="space-y-4 pt-4 border-t">
        <div className="flex items-start space-x-3">
          <Checkbox
            id="consent_data"
            checked={formData.consent_data}
            onCheckedChange={(checked) => setFormData({ ...formData, consent_data: checked })}
            data-testid="consent-data"
          />
          <Label htmlFor="consent_data" className="text-sm leading-relaxed cursor-pointer">
            Autorizo o tratamento dos meus dados pessoais para análise do meu pedido de crédito/imobiliário, nos termos do RGPD.
          </Label>
        </div>
        <div className="flex items-start space-x-3">
          <Checkbox
            id="consent_contact"
            checked={formData.consent_contact}
            onCheckedChange={(checked) => setFormData({ ...formData, consent_contact: checked })}
            data-testid="consent-contact"
          />
          <Label htmlFor="consent_contact" className="text-sm leading-relaxed cursor-pointer">
            Autorizo ser contactado por telefone, email ou SMS para dar seguimento ao meu pedido.
          </Label>
        </div>
      </div>
    </div>
  );

  const renderSuccess = () => (
    <div className="text-center py-12">
      <div className="h-20 w-20 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-6">
        <Check className="h-10 w-10 text-emerald-600" />
      </div>
      <h2 className="text-2xl font-bold mb-2">Registo Enviado com Sucesso!</h2>
      <p className="text-muted-foreground mb-6 max-w-md mx-auto">
        Obrigado pelo seu interesse. A nossa equipa irá analisar o seu pedido e entrará em contacto consigo brevemente.
      </p>
      <div className="bg-muted/50 p-4 rounded-lg max-w-sm mx-auto">
        <p className="text-sm text-muted-foreground">
          <strong>Próximos passos:</strong><br />
          Um consultor irá contactá-lo dentro de 24-48 horas úteis para dar seguimento ao seu processo.
        </p>
      </div>
    </div>
  );

  const canProceed = () => {
    switch (step) {
      case 1:
        return !!formData.process_type;
      case 2:
        return formData.name && formData.email && formData.phone && formData.nif;
      case 3:
        return formData.monthly_income && formData.employment_type;
      case 4:
        return formData.consent_data && formData.consent_contact;
      default:
        return false;
    }
  };

  if (submitted) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-4">
        <Card className="w-full max-w-2xl border-border">
          <CardContent className="p-8">
            {renderSuccess()}
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center gap-3">
          <Building2 className="h-8 w-8 text-primary" />
          <div>
            <h1 className="text-xl font-bold tracking-tight">CreditoIMO</h1>
            <p className="text-sm text-muted-foreground">Registo de Cliente</p>
          </div>
        </div>
      </header>

      {/* Form */}
      <main className="max-w-3xl mx-auto px-4 py-8">
        <Card className="border-border">
          <CardHeader className="text-center border-b">
            <CardTitle>Formulário de Registo</CardTitle>
            <CardDescription>
              Preencha os seus dados para iniciar o processo de {formData.process_type === "credito" ? "crédito" : formData.process_type === "imobiliaria" ? "procura de imóvel" : formData.process_type === "ambos" ? "crédito e imobiliária" : "análise"}
            </CardDescription>
          </CardHeader>
          <CardContent className="p-6 md:p-8">
            {renderStepIndicator()}

            {step === 1 && renderStep1()}
            {step === 2 && renderStep2()}
            {step === 3 && renderStep3()}
            {step === 4 && renderStep4()}

            <div className="flex justify-between mt-8 pt-6 border-t">
              <Button
                variant="outline"
                onClick={() => step === 1 ? navigate("/") : setStep(step - 1)}
                data-testid="back-btn"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                {step === 1 ? "Voltar" : "Anterior"}
              </Button>

              {step < 4 ? (
                <Button
                  onClick={() => {
                    if (!canProceed()) {
                      toast.error("Por favor, preencha os campos obrigatórios");
                      return;
                    }
                    setStep(step + 1);
                  }}
                  data-testid="next-btn"
                >
                  Próximo
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              ) : (
                <Button 
                  onClick={handleSubmit} 
                  disabled={loading || !canProceed()} 
                  data-testid="submit-btn"
                >
                  {loading ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      A enviar...
                    </>
                  ) : (
                    <>
                      <Check className="h-4 w-4 mr-2" />
                      Enviar Registo
                    </>
                  )}
                </Button>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Staff login link */}
        <p className="text-center text-sm text-muted-foreground mt-6">
          É colaborador?{" "}
          <a href="/login" className="text-primary hover:underline">
            Aceder ao sistema
          </a>
        </p>
      </main>
    </div>
  );
};

export default PublicClientForm;
