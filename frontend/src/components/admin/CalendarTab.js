/**
 * CalendarTab - Componente de Calendário para Admin Dashboard
 */
import { useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card";
import { Button } from "../ui/button";
import { Badge } from "../ui/badge";
import { Label } from "../ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../ui/select";
import { Calendar } from "../ui/calendar";
import { Plus, Trash2, Eye, Clock as ClockIcon } from "lucide-react";

const priorityOrder = { high: 1, medium: 2, low: 3 };
const priorityLabels = { high: "Alta", medium: "Média", low: "Baixa" };
const priorityColors = {
  high: "bg-red-100 text-red-800 border-red-200",
  medium: "bg-yellow-100 text-yellow-800 border-yellow-200",
  low: "bg-green-100 text-green-800 border-green-200"
};

const CalendarTab = ({ 
  calendarDeadlines, 
  consultors, 
  intermediarios, 
  users,
  onCreateEvent,
  onDeleteEvent 
}) => {
  const navigate = useNavigate();
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [priorityFilter, setPriorityFilter] = useState("all");
  const [consultorFilter, setConsultorFilter] = useState("all");
  const [mediadorFilter, setMediadorFilter] = useState("all");

  // Ordenar e filtrar eventos do calendário
  const sortedCalendarDeadlines = useMemo(() => {
    let filtered = [...calendarDeadlines];
    
    if (priorityFilter !== "all") {
      filtered = filtered.filter(d => d.priority === priorityFilter);
    }
    
    return filtered.sort((a, b) => {
      const dateCompare = new Date(a.due_date) - new Date(b.due_date);
      if (dateCompare !== 0) return dateCompare;
      return (priorityOrder[a.priority] || 3) - (priorityOrder[b.priority] || 3);
    });
  }, [calendarDeadlines, priorityFilter]);

  // Próximos 7 prazos
  const upcomingDeadlines = useMemo(() => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    return sortedCalendarDeadlines
      .filter(d => new Date(d.due_date) >= today)
      .slice(0, 7);
  }, [sortedCalendarDeadlines]);

  // Prazos para a data selecionada
  const deadlinesForDate = useMemo(() => {
    const dateStr = selectedDate.toISOString().split('T')[0];
    return sortedCalendarDeadlines
      .filter(d => d.due_date === dateStr)
      .sort((a, b) => (priorityOrder[a.priority] || 3) - (priorityOrder[b.priority] || 3));
  }, [sortedCalendarDeadlines, selectedDate]);

  // Datas com prazos para highlight no calendário
  const datesWithDeadlines = useMemo(() => {
    return calendarDeadlines.map(d => new Date(d.due_date));
  }, [calendarDeadlines]);

  const getUserName = (userId) => {
    const user = users.find(u => u.id === userId);
    return user ? user.name : "-";
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Calendário e Filtros */}
      <Card className="border-border lg:col-span-1">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg">Calendário</CardTitle>
            <Button size="sm" onClick={() => onCreateEvent(selectedDate)}>
              <Plus className="h-4 w-4 mr-1" />Evento
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <Calendar
            mode="single"
            selected={selectedDate}
            onSelect={(date) => date && setSelectedDate(date)}
            className="rounded-md border"
            modifiers={{ hasDeadline: datesWithDeadlines }}
            modifiersStyles={{ hasDeadline: { backgroundColor: "rgb(254 202 202)", fontWeight: "bold" } }}
          />
          
          {/* Filtros */}
          <div className="space-y-3 pt-4 border-t">
            <h4 className="font-medium text-sm">Filtros</h4>
            <div className="space-y-2">
              <Label className="text-xs">Prioridade</Label>
              <Select value={priorityFilter} onValueChange={setPriorityFilter}>
                <SelectTrigger className="h-8 text-sm"><SelectValue placeholder="Todas" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todas as prioridades</SelectItem>
                  <SelectItem value="high">🔴 Alta</SelectItem>
                  <SelectItem value="medium">🟡 Média</SelectItem>
                  <SelectItem value="low">🟢 Baixa</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label className="text-xs">Consultor</Label>
              <Select value={consultorFilter} onValueChange={setConsultorFilter}>
                <SelectTrigger className="h-8 text-sm"><SelectValue placeholder="Todos" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos</SelectItem>
                  {consultors.map((c) => (<SelectItem key={c.id} value={c.id}>{c.name}</SelectItem>))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label className="text-xs">Intermediário</Label>
              <Select value={mediadorFilter} onValueChange={setMediadorFilter}>
                <SelectTrigger className="h-8 text-sm"><SelectValue placeholder="Todos" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos</SelectItem>
                  {intermediarios.map((m) => (<SelectItem key={m.id} value={m.id}>{m.name}</SelectItem>))}
                </SelectContent>
              </Select>
            </div>
          </div>
          
          {/* Próximos Prazos */}
          <div className="space-y-3 pt-4 border-t">
            <h4 className="font-medium text-sm flex items-center gap-2">
              <ClockIcon className="h-4 w-4" />
              Próximos Prazos
            </h4>
            {upcomingDeadlines.length === 0 ? (
              <p className="text-xs text-muted-foreground">Sem prazos próximos</p>
            ) : (
              <div className="space-y-2">
                {upcomingDeadlines.map((deadline) => {
                  const daysUntil = Math.ceil((new Date(deadline.due_date) - new Date()) / (1000 * 60 * 60 * 24));
                  return (
                    <div 
                      key={deadline.id} 
                      className={`p-2 rounded border text-xs cursor-pointer hover:opacity-80 ${priorityColors[deadline.priority] || 'bg-gray-50'}`}
                      onClick={() => setSelectedDate(new Date(deadline.due_date))}
                    >
                      <div className="flex justify-between items-start">
                        <span className="font-medium truncate flex-1">{deadline.title}</span>
                        <Badge variant="outline" className="ml-1 text-[10px] shrink-0">
                          {daysUntil === 0 ? 'Hoje' : daysUntil === 1 ? 'Amanhã' : `${daysUntil}d`}
                        </Badge>
                      </div>
                      <p className="text-[10px] text-muted-foreground mt-1">
                        {new Date(deadline.due_date).toLocaleDateString('pt-PT', { day: 'numeric', month: 'short' })}
                      </p>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Detalhes do Dia */}
      <Card className="border-border lg:col-span-2">
        <CardHeader>
          <CardTitle className="text-lg">
            Prazos - {selectedDate.toLocaleDateString('pt-PT', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })}
          </CardTitle>
          <CardDescription>
            {deadlinesForDate.length} prazo(s) nesta data
            {priorityFilter !== "all" && ` (filtro: ${priorityLabels[priorityFilter]})`}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {deadlinesForDate.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <p>Nenhum prazo para esta data</p>
              <Button variant="outline" className="mt-4" onClick={() => onCreateEvent(selectedDate)}>
                <Plus className="h-4 w-4 mr-2" />Criar Evento
              </Button>
            </div>
          ) : (
            <div className="space-y-3">
              {deadlinesForDate.map((deadline) => (
                <div key={deadline.id} className="flex items-center justify-between p-4 bg-muted/30 rounded-lg">
                  <div className="space-y-1">
                    <p className="font-medium">{deadline.title}</p>
                    <p className="text-sm text-muted-foreground">
                      {deadline.client_name !== "Evento Geral" ? `Cliente: ${deadline.client_name}` : "Evento Geral"}
                    </p>
                    <div className="flex gap-2 mt-2 flex-wrap">
                      {deadline.assigned_consultor_id && (
                        <Badge variant="outline" className="text-xs bg-blue-50">Consultor: {getUserName(deadline.assigned_consultor_id)}</Badge>
                      )}
                      {deadline.assigned_mediador_id && (
                        <Badge variant="outline" className="text-xs bg-emerald-50">Mediador: {getUserName(deadline.assigned_mediador_id)}</Badge>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge className={deadline.priority === "high" ? "bg-red-100 text-red-800" : deadline.priority === "medium" ? "bg-yellow-100 text-yellow-800" : "bg-green-100 text-green-800"}>
                      {priorityLabels[deadline.priority] || deadline.priority}
                    </Badge>
                    {deadline.process_id && (
                      <Button variant="ghost" size="icon" onClick={() => navigate(`/process/${deadline.process_id}`)}>
                        <Eye className="h-4 w-4" />
                      </Button>
                    )}
                    <Button variant="ghost" size="icon" onClick={() => onDeleteEvent(deadline.id)}>
                      <Trash2 className="h-4 w-4 text-destructive" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default CalendarTab;
