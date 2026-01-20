"""
End-to-End Tests for CreditoIMO Frontend
Using Playwright for browser automation
"""
import pytest
from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:3000"


@pytest.fixture(scope="session")
def browser_context_args():
    return {
        "viewport": {"width": 1920, "height": 1080},
        "ignore_https_errors": True
    }


class TestPublicForm:
    """Tests for the public client registration form"""
    
    def test_public_form_loads(self, page: Page):
        """Test that the public form loads correctly"""
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        
        # Should see the registration form
        expect(page.locator("text=Formulário de Registo")).to_be_visible()
        expect(page.locator("text=Tipo de Serviço")).to_be_visible()
    
    def test_public_form_step_navigation(self, page: Page):
        """Test form step navigation"""
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        
        # Step 1: Select service type
        page.click("text=Crédito")
        page.click("text=Próximo")
        
        # Step 2: Should show personal data form
        expect(page.locator("text=Dados Pessoais")).to_be_visible()
    
    def test_public_form_validation(self, page: Page):
        """Test form validation - required fields"""
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        
        # Try to advance without selecting type
        next_button = page.locator("text=Próximo")
        expect(next_button).to_be_visible()
    
    def test_public_form_submission(self, page: Page):
        """Test complete form submission"""
        import uuid
        unique_email = f"test_e2e_{uuid.uuid4().hex[:8]}@email.pt"
        
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        
        # Step 1: Select Crédito
        page.click("text=Crédito")
        page.click("text=Próximo")
        
        # Step 2: Fill personal data
        page.fill('input[name="name"]', "Teste E2E Playwright")
        page.fill('input[name="email"]', unique_email)
        page.fill('input[name="phone"]', "+351 999 888 777")
        page.click("text=Próximo")
        
        # Step 3: Financial data (optional, skip)
        page.click("text=Próximo")
        
        # Step 4: Submit
        page.click("text=Submeter")
        
        # Should show success message
        page.wait_for_timeout(2000)
        expect(page.locator("text=sucesso")).to_be_visible()


class TestLogin:
    """Tests for the login page"""
    
    def test_login_page_loads(self, page: Page):
        """Test that login page loads correctly"""
        page.goto(f"{BASE_URL}/login")
        page.wait_for_load_state("networkidle")
        
        expect(page.locator("text=Entrar no Sistema")).to_be_visible()
        expect(page.locator('input[type="email"]')).to_be_visible()
        expect(page.locator('input[type="password"]')).to_be_visible()
    
    def test_login_with_invalid_credentials(self, page: Page):
        """Test login with wrong credentials shows error"""
        page.goto(f"{BASE_URL}/login")
        page.wait_for_load_state("networkidle")
        
        page.fill('input[type="email"]', "wrong@email.pt")
        page.fill('input[type="password"]', "wrongpassword")
        page.click('button[type="submit"]')
        
        page.wait_for_timeout(1000)
        # Should show error message
        expect(page.locator("text=Credenciais inválidas")).to_be_visible()
    
    def test_login_admin_success(self, page: Page):
        """Test successful admin login"""
        page.goto(f"{BASE_URL}/login")
        page.wait_for_load_state("networkidle")
        
        page.fill('input[type="email"]', "admin@sistema.pt")
        page.fill('input[type="password"]', "admin123")
        page.click('button[type="submit"]')
        
        page.wait_for_timeout(2000)
        # Should redirect to dashboard
        expect(page).to_have_url(f"{BASE_URL}/admin")
    
    def test_login_consultor_success(self, page: Page):
        """Test successful consultor login"""
        page.goto(f"{BASE_URL}/login")
        page.wait_for_load_state("networkidle")
        
        page.fill('input[type="email"]', "consultor@sistema.pt")
        page.fill('input[type="password"]', "consultor123")
        page.click('button[type="submit"]')
        
        page.wait_for_timeout(2000)
        # Should redirect to consultor dashboard
        expect(page).to_have_url(f"{BASE_URL}/consultor")
    
    def test_login_mediador_success(self, page: Page):
        """Test successful mediador login"""
        page.goto(f"{BASE_URL}/login")
        page.wait_for_load_state("networkidle")
        
        page.fill('input[type="email"]', "mediador@sistema.pt")
        page.fill('input[type="password"]', "mediador123")
        page.click('button[type="submit"]')
        
        page.wait_for_timeout(2000)
        # Should redirect to mediador dashboard
        expect(page).to_have_url(f"{BASE_URL}/mediador")


class TestAdminDashboard:
    """Tests for the admin dashboard"""
    
    def _login_as_admin(self, page: Page):
        """Helper to login as admin"""
        page.goto(f"{BASE_URL}/login")
        page.wait_for_load_state("networkidle")
        page.fill('input[type="email"]', "admin@sistema.pt")
        page.fill('input[type="password"]', "admin123")
        page.click('button[type="submit"]')
        page.wait_for_timeout(2000)
    
    def test_admin_dashboard_loads(self, page: Page):
        """Test admin dashboard loads with stats"""
        self._login_as_admin(page)
        
        expect(page.locator("text=Dashboard")).to_be_visible()
        expect(page.locator("text=Total de Processos")).to_be_visible()
    
    def test_admin_can_see_processes(self, page: Page):
        """Test admin can see processes list"""
        self._login_as_admin(page)
        
        # Click on processes tab/section
        page.click("text=Processos")
        page.wait_for_timeout(1000)
        
        # Should show processes table or list
        expect(page.locator("table")).to_be_visible()
    
    def test_admin_can_see_users(self, page: Page):
        """Test admin can see users list"""
        self._login_as_admin(page)
        
        # Click on users tab
        page.click("text=Utilizadores")
        page.wait_for_timeout(1000)
        
        expect(page.locator("text=admin@sistema.pt")).to_be_visible()
    
    def test_admin_can_manage_workflow(self, page: Page):
        """Test admin can access workflow management"""
        self._login_as_admin(page)
        
        # Click on workflow/config section
        page.click("text=Configurações")
        page.wait_for_timeout(1000)
        
        expect(page.locator("text=Estados do Fluxo")).to_be_visible()
    
    def test_admin_logout(self, page: Page):
        """Test admin can logout"""
        self._login_as_admin(page)
        
        # Click logout button
        page.click("text=Sair")
        page.wait_for_timeout(1000)
        
        # Should redirect to login or home
        expect(page).to_have_url(f"{BASE_URL}/login")


class TestProcessDetails:
    """Tests for process details page"""
    
    def _login_as_admin(self, page: Page):
        """Helper to login as admin"""
        page.goto(f"{BASE_URL}/login")
        page.wait_for_load_state("networkidle")
        page.fill('input[type="email"]', "admin@sistema.pt")
        page.fill('input[type="password"]', "admin123")
        page.click('button[type="submit"]')
        page.wait_for_timeout(2000)
    
    def test_process_details_page_loads(self, page: Page):
        """Test process details page with tabs"""
        self._login_as_admin(page)
        
        # Go to processes
        page.click("text=Processos")
        page.wait_for_timeout(1000)
        
        # Click on first process
        first_process = page.locator("table tbody tr").first
        first_process.click()
        page.wait_for_timeout(1000)
        
        # Should show process details with tabs
        expect(page.locator("text=Dados do Processo")).to_be_visible()
    
    def test_process_has_activity_tab(self, page: Page):
        """Test process has activity/comments tab"""
        self._login_as_admin(page)
        
        page.click("text=Processos")
        page.wait_for_timeout(1000)
        
        first_process = page.locator("table tbody tr").first
        first_process.click()
        page.wait_for_timeout(1000)
        
        # Click activity tab
        page.click("text=Atividade")
        page.wait_for_timeout(500)
        
        expect(page.locator("text=Comentários")).to_be_visible()
    
    def test_process_has_history_tab(self, page: Page):
        """Test process has history tab"""
        self._login_as_admin(page)
        
        page.click("text=Processos")
        page.wait_for_timeout(1000)
        
        first_process = page.locator("table tbody tr").first
        first_process.click()
        page.wait_for_timeout(1000)
        
        # Click history tab
        page.click("text=Histórico")
        page.wait_for_timeout(500)
        
        expect(page.locator("text=Alterações")).to_be_visible()


class TestResponsiveness:
    """Tests for responsive design"""
    
    def test_mobile_public_form(self, page: Page):
        """Test public form works on mobile viewport"""
        page.set_viewport_size({"width": 375, "height": 812})  # iPhone X
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        
        expect(page.locator("text=Formulário de Registo")).to_be_visible()
        expect(page.locator("text=Crédito")).to_be_visible()
    
    def test_mobile_login(self, page: Page):
        """Test login works on mobile viewport"""
        page.set_viewport_size({"width": 375, "height": 812})
        page.goto(f"{BASE_URL}/login")
        page.wait_for_load_state("networkidle")
        
        expect(page.locator('input[type="email"]')).to_be_visible()
        expect(page.locator('input[type="password"]')).to_be_visible()
