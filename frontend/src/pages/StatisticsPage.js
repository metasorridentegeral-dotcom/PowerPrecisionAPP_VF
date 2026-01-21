import { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import DashboardLayout from "../layouts/DashboardLayout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { 
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, 
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer 
} from "recharts";
import { 
  TrendingUp, TrendingDown, Users, FileText, CheckCircle, 
  Clock, AlertCircle, Euro, Calendar, Target
} from "lucide-react";
import { getStats, getProcesses, getUsers } from "../services/api";
import { toast } from "sonner";

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

const StatisticsPage = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({});
  const [processes, setProcesses] = useState([]);
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(user?.id);
  const [timeRange, setTimeRange] = useState("30");

  const canViewAllStats = user?.role === "admin" || user?.role === "ceo";

  useEffect(() => {
    fetchData();
  }, [selectedUser, timeRange]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [statsRes, processesRes, usersRes] = await Promise.all([
        getStats(),
        getProcesses(),
        canViewAllStats ? getUsers() : Promise.resolve({ data: [] })
      ]);

      setStats(statsRes.data);
      setProcesses(processesRes.data);
      setUsers(usersRes.data);
    } catch (error) {
      toast.error("Erro ao carregar estatísticas");
    } finally {
      setLoading(false);
    }
  };

  // Filtrar processos baseado no utilizador selecionado
  const filteredProcesses = processes.filter(p => {
    if (!canViewAllStats || selectedUser === "all") return true;
    return p.assigned_consultor === selectedUser || p.assigned_intermediario === selectedUser;
  });

  // Calcular estatísticas personalizadas
  const totalProcessos = filteredProcesses.length;
  const processosAtivos = filteredProcesses.filter(p => !['concluidos', 'desistencias'].includes(p.status)).length;
  const processosConcluidos = filteredProcesses.filter(p => p.status === 'concluidos').length;
  const desistencias = filteredProcesses.filter(p => p.status === 'desistencias').length;
  
  const valorTotal = filteredProcesses.reduce((sum, p) => sum + (p.property_value || 0), 0);
  const valorMedio = totalProcessos > 0 ? valorTotal / totalProcessos : 0;
  
  const taxaSucesso = totalProcessos > 0 
    ? ((processosConcluidos / (processosConcluidos + desistencias)) * 100).toFixed(1)
    : 0;

  // Dados para gráficos
  const statusData = Object.entries(
    filteredProcesses.reduce((acc, p) => {
      acc[p.status] = (acc[p.status] || 0) + 1;
      return acc;
    }, {})
  ).map(([name, value]) => ({ name, value }));

  const prioridadeData = [
    { name: 'Alta', value: filteredProcesses.filter(p => p.priority === 'high').length },
    { name: 'Média', value: filteredProcesses.filter(p => p.priority === 'medium').length },
    { name: 'Baixa', value: filteredProcesses.filter(p => p.priority === 'low').length },
  ].filter(d => d.value > 0);

  const valorPorFaseData = Object.entries(
    filteredProcesses.reduce((acc, p) => {
      if (!acc[p.status]) acc[p.status] = 0;
      acc[p.status] += p.property_value || 0;
      return acc;
    }, {})
  ).map(([name, value]) => ({ 
    name, 
    value: Math.round(value / 1000) // em milhares
  })).slice(0, 10);

  return (
    <DashboardLayout title="Estatísticas e Análise">
      <div className="space-y-6 p-6">
        {/* Filtros */}
        <div className="flex flex-wrap gap-4">
          {canViewAllStats && (
            <Select value={selectedUser} onValueChange={setSelectedUser}>
              <SelectTrigger className="w-64">
                <SelectValue placeholder="Selecionar utilizador" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos os Utilizadores</SelectItem>
                {users.map(u => (
                  <SelectItem key={u.id} value={u.id}>{u.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
          
          <Select value={timeRange} onValueChange={setTimeRange}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="Período" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7">Últimos 7 dias</SelectItem>
              <SelectItem value="30">Últimos 30 dias</SelectItem>
              <SelectItem value="90">Últimos 90 dias</SelectItem>
              <SelectItem value="365">Último ano</SelectItem>
              <SelectItem value="all">Todo o período</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* KPIs Principais */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Total de Processos</CardTitle>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{totalProcessos}</div>
              <p className="text-xs text-muted-foreground mt-1">
                {processosAtivos} ativos
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Taxa de Sucesso</CardTitle>
              <Target className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{taxaSucesso}%</div>
              <p className="text-xs text-muted-foreground mt-1">
                {processosConcluidos} concluídos vs {desistencias} desistências
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Valor Total</CardTitle>
              <Euro className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                €{(valorTotal / 1000000).toFixed(1)}M
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                Média: €{Math.round(valorMedio / 1000)}k
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Em Progresso</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{processosAtivos}</div>
              <p className="text-xs text-muted-foreground mt-1">
                {((processosAtivos / totalProcessos) * 100).toFixed(0)}% do total
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Gráficos */}
        <Tabs defaultValue="status" className="space-y-4">
          <TabsList>
            <TabsTrigger value="status">Por Fase</TabsTrigger>
            <TabsTrigger value="priority">Por Prioridade</TabsTrigger>
            <TabsTrigger value="value">Valor por Fase</TabsTrigger>
          </TabsList>

          <TabsContent value="status" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Distribuição por Fase</CardTitle>
                <CardDescription>
                  Número de processos em cada fase do workflow
                </CardDescription>
              </CardHeader>
              <CardContent className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={statusData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="value" fill="#3b82f6" name="Processos" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="priority" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Distribuição por Prioridade</CardTitle>
                <CardDescription>
                  Processos organizados por nível de prioridade
                </CardDescription>
              </CardHeader>
              <CardContent className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={prioridadeData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={(entry) => `${entry.name}: ${entry.value}`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {prioridadeData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="value" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Valor por Fase (em milhares €)</CardTitle>
                <CardDescription>
                  Valor total de imóveis em cada fase
                </CardDescription>
              </CardHeader>
              <CardContent className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={valorPorFaseData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="value" fill="#10b981" name="Valor (k€)" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  );
};

export default StatisticsPage;
