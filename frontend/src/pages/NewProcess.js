import { useState } from "react";
import { useNavigate } from "react-router-dom";
import DashboardLayout from "../layouts/DashboardLayout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Textarea } from "../components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";
import { RadioGroup, RadioGroupItem } from "../components/ui/radio-group";
import { createProcess } from "../services/api";
import { Building2, CreditCard, FileText, Loader2, ArrowLeft, ArrowRight, Check } from "lucide-react";
import { toast } from "sonner";

const NewProcess = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [processType, setProcessType] = useState("");
  const [personalData, setPersonalData] = useState({
    nif: "",
    address: "",
    birth_date: "",
    marital_status: "",
    nationality: "",
  });
  const [financialData, setFinancialData] = useState({
    monthly_income: "",
    other_income: "",
    monthly_expenses: "",
    employment_type: "",
    employer_name: "",
    employment_duration: "",
    has_debts: false,
    debt_amount: "",
  });

  const handleSubmit = async () => {
    if (!processType) {
      toast.error("Selecione o tipo de processo");
      return;
    }

    setLoading(true);

    try {
      const data = {
        process_type: processType,
        personal_data: personalData,
        financial_data: {
          ...financialData,
          monthly_income: financialData.monthly_income ? parseFloat(financialData.monthly_income) : null,
          other_income: financialData.other_income ? parseFloat(financialData.other_income) : null,
          monthly_expenses: financialData.monthly_expenses ? parseFloat(financialData.monthly_expenses) : null,
          debt_amount: financialData.debt_amount ? parseFloat(financialData.debt_amount) : null,
        },
      };

      await createProcess(data);
      toast.success("Processo criado com sucesso!");
      navigate("/cliente");
    } catch (error) {
      console.error("Error creating process:", error);
      toast.error(error.response?.data?.detail || "Erro ao criar processo");
    } finally {
      setLoading(false);
    }
  };

  const renderStepIndicator = () => (
    <div className="flex items-center justify-center mb-8">
      {[1, 2, 3].map((s) => (
        <div key={s} className="flex items-center">
          <div
            className={`h-10 w-10 rounded-full flex items-center justify-center text-sm font-semibold ${
              s < step
                ? "bg-emerald-500 text-white"
                : s === step
                ? "bg-primary text-primary-foreground"
                : "bg-muted text-muted-foreground"
            }`}
          >
            {s < step ? <Check className="h-5 w-5" /> : s}
          </div>
          {s < 3 && (
            <div
              className={`h-1 w-16 mx-2 ${
                s < step ? "bg-emerald-500" : "bg-muted"
              }`}
            />
          )}
        </div>
      ))}
    </div>
  );

  const renderStep1 = () => (
    <div className="space-y-6">
      <div className="text-center mb-6">
        <h2 className="text-xl font-semibold mb-2">Tipo de Processo</h2>
        <p className="text-muted-foreground">
          Selecione o tipo de ajuda que precisa
        </p>
      </div>
      <RadioGroup
        value={processType}
        onValueChange={setProcessType}
        className="grid grid-cols-1 md:grid-cols-3 gap-4"
      >
        <div>
          <RadioGroupItem
            value="credito"
            id="credito"
            className="peer sr-only"
          />
          <Label
            htmlFor="credito"
            className="flex flex-col items-center justify-center p-6 border-2 rounded-md cursor-pointer transition-all peer-data-[state=checked]:border-primary peer-data-[state=checked]:bg-primary/5 hover:bg-muted/50"
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
          <RadioGroupItem
            value="imobiliaria"
            id="imobiliaria"
            className="peer sr-only"
          />
          <Label
            htmlFor="imobiliaria"
            className="flex flex-col items-center justify-center p-6 border-2 rounded-md cursor-pointer transition-all peer-data-[state=checked]:border-primary peer-data-[state=checked]:bg-primary/5 hover:bg-muted/50"
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
            className="flex flex-col items-center justify-center p-6 border-2 rounded-md cursor-pointer transition-all peer-data-[state=checked]:border-primary peer-data-[state=checked]:bg-primary/5 hover:bg-muted/50"
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
        <h2 className="text-xl font-semibold mb-2">Dados Pessoais</h2>
        <p className="text-muted-foreground">
          Preencha os seus dados pessoais
        </p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="nif">NIF</Label>
          <Input
            id="nif"
            placeholder="123456789"
            value={personalData.nif}
            onChange={(e) =>
              setPersonalData({ ...personalData, nif: e.target.value })
            }
            data-testid="personal-nif"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="birth_date">Data de Nascimento</Label>
          <Input
            id="birth_date"
            type="date"
            value={personalData.birth_date}
            onChange={(e) =>
              setPersonalData({ ...personalData, birth_date: e.target.value })
            }
            data-testid="personal-birth-date"
          />
        </div>
        <div className="space-y-2 md:col-span-2">
          <Label htmlFor="address">Morada</Label>
          <Input
            id="address"
            placeholder="Rua, número, código postal, cidade"
            value={personalData.address}
            onChange={(e) =>
              setPersonalData({ ...personalData, address: e.target.value })
            }
            data-testid="personal-address"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="marital_status">Estado Civil</Label>
          <Select
            value={personalData.marital_status}
            onValueChange={(value) =>
              setPersonalData({ ...personalData, marital_status: value })
            }
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
          <Label htmlFor="nationality">Nacionalidade</Label>
          <Input
            id="nationality"
            placeholder="Portuguesa"
            value={personalData.nationality}
            onChange={(e) =>
              setPersonalData({ ...personalData, nationality: e.target.value })
            }
            data-testid="personal-nationality"
          />
        </div>
      </div>
    </div>
  );

  const renderStep3 = () => (
    <div className="space-y-6">
      <div className="text-center mb-6">
        <h2 className="text-xl font-semibold mb-2">Dados Financeiros</h2>
        <p className="text-muted-foreground">
          Preencha os seus dados financeiros
        </p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="monthly_income">Rendimento Mensal (€)</Label>
          <Input
            id="monthly_income"
            type="number"
            placeholder="0.00"
            value={financialData.monthly_income}
            onChange={(e) =>
              setFinancialData({ ...financialData, monthly_income: e.target.value })
            }
            data-testid="financial-monthly-income"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="other_income">Outros Rendimentos (€)</Label>
          <Input
            id="other_income"
            type="number"
            placeholder="0.00"
            value={financialData.other_income}
            onChange={(e) =>
              setFinancialData({ ...financialData, other_income: e.target.value })
            }
            data-testid="financial-other-income"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="monthly_expenses">Despesas Mensais (€)</Label>
          <Input
            id="monthly_expenses"
            type="number"
            placeholder="0.00"
            value={financialData.monthly_expenses}
            onChange={(e) =>
              setFinancialData({ ...financialData, monthly_expenses: e.target.value })
            }
            data-testid="financial-monthly-expenses"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="employment_type">Tipo de Emprego</Label>
          <Select
            value={financialData.employment_type}
            onValueChange={(value) =>
              setFinancialData({ ...financialData, employment_type: value })
            }
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
          <Label htmlFor="employer_name">Nome da Entidade Empregadora</Label>
          <Input
            id="employer_name"
            placeholder="Empresa XYZ"
            value={financialData.employer_name}
            onChange={(e) =>
              setFinancialData({ ...financialData, employer_name: e.target.value })
            }
            data-testid="financial-employer-name"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="employment_duration">Tempo de Emprego</Label>
          <Input
            id="employment_duration"
            placeholder="Ex: 2 anos"
            value={financialData.employment_duration}
            onChange={(e) =>
              setFinancialData({ ...financialData, employment_duration: e.target.value })
            }
            data-testid="financial-employment-duration"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="has_debts">Tem dívidas?</Label>
          <Select
            value={financialData.has_debts ? "yes" : "no"}
            onValueChange={(value) =>
              setFinancialData({ ...financialData, has_debts: value === "yes" })
            }
          >
            <SelectTrigger data-testid="financial-has-debts">
              <SelectValue placeholder="Selecione" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="no">Não</SelectItem>
              <SelectItem value="yes">Sim</SelectItem>
            </SelectContent>
          </Select>
        </div>
        {financialData.has_debts && (
          <div className="space-y-2">
            <Label htmlFor="debt_amount">Valor das Dívidas (€)</Label>
            <Input
              id="debt_amount"
              type="number"
              placeholder="0.00"
              value={financialData.debt_amount}
              onChange={(e) =>
                setFinancialData({ ...financialData, debt_amount: e.target.value })
              }
              data-testid="financial-debt-amount"
            />
          </div>
        )}
      </div>
    </div>
  );

  return (
    <DashboardLayout title="Novo Processo">
      <Card className="max-w-3xl mx-auto border-border">
        <CardContent className="p-6 md:p-8">
          {renderStepIndicator()}

          {step === 1 && renderStep1()}
          {step === 2 && renderStep2()}
          {step === 3 && renderStep3()}

          <div className="flex justify-between mt-8">
            <Button
              variant="outline"
              onClick={() => (step === 1 ? navigate("/cliente") : setStep(step - 1))}
              data-testid="back-btn"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              {step === 1 ? "Cancelar" : "Voltar"}
            </Button>

            {step < 3 ? (
              <Button
                onClick={() => {
                  if (step === 1 && !processType) {
                    toast.error("Selecione o tipo de processo");
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
              <Button onClick={handleSubmit} disabled={loading} data-testid="submit-btn">
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    A criar...
                  </>
                ) : (
                  <>
                    <Check className="h-4 w-4 mr-2" />
                    Criar Processo
                  </>
                )}
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </DashboardLayout>
  );
};

export default NewProcess;
