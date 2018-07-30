import Vue from 'vue'
import Router from 'vue-router'
import Login from '../components/login/Login.vue'
import Users from '../components/users/Users.vue'
import User from '../components/user/User.vue'
import Positions from '../components/positions/Positions.vue'
import auth from '../auth/auth'
import apolloClient from '../apollo-client.js'
import Reports from '../components/reports/Reports.vue'
import Report from '../components/report/Report.vue'
import GIPReports from '../components/reports/GIPReports.vue'
import GIPReport from '../components/report/GIPReport.vue'
import Coefficients from '../components/user_coefficients/Coefficients.vue'
import Bonuses from '../components/bonuses/Bonuses.vue'
import Projects from '../components/projects/Projects'
import Absences from '../components/absences/Absences.vue'
import Stats from '../components/stats/Stats.vue'
import Salary from '../components/salary/Salary.vue'
import UserSalary from '../components/salary/UserSalary.vue'
import Fillout from '../components/fillout/Fillout'
import Storage from '../components/storage/Storage'
import Manufacturers from '../components/manufacturers/Manufacturers'
import GoodKinds from '../components/storage/GoodKinds'
import BuyApplication from '../components/logistics/BuyApplication'
import TransferRequest from '../components/logistics/TransferRequest'
import TransferRequestsList from '../components/logistics/TransferRequestsList'
import Page404 from '../components/page404/page404.vue'
import ReplaceUser from '../components/replace_user/ReplaceUser.vue'
import Orders from '../components/orders/Orders'
import ProjectAnalysis from '../components/project_analysis/ProjectAnalysis'
import B7Export from '../components/salary/B7Export'
import Tasks from '../components/tasks/Tasks'
import Help from '../components/help/Help'
import ProjectPies from '../components/data_tree/ProjectPies'
import ProjectStateChange from '../components/project_state_change/ProjectStateChange'
import RegistryCollisionsStateProjects from '../components/registry_collisions_state_projects/RegistryCollisionsStateProjects'
import Specification from '../components/storage/Specification'
import SpecificationsPositions from '../components/storage/SpecificationsPositions'
import Clients from '../components/clients/Clients'
import Contacts from '../components/clients/Contacts'
import ClientHistory from '../components/clients/ClientHistory'
import MyNotifications from '../components/notice/MyNotifications'
import FinancialInfo from '../components/financial_info/FinancialInfo'
import FinancialInfoHistory from '../components/financial_info/FinancialInfoHistory'
import SalaryPayment from '../components/salary_payment/SalaryPayment'
import PositionBind from '../components/positions/PositionBind'
import Accruals from '../components/salary/Accruals'
import LogisticsRequest from '../components/logistics/LogisticsRequest'
import LogisticDelivery from '../components/logistics/LogisticDelivery'

Vue.use(Router)

const router = new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      name: 'default',
      redirect: { name: 'reports' }
    },
    {
      path: '/login',
      name: 'login',
      component: Login
    },
    {
      path: '/users',
      name: 'users',
      component: Users
    },
    {
      path: '/user/:id',
      name: 'user',
      component: User
    },
    {
      path: '/positions',
      name: 'positions',
      component: Positions
    },
    {
      path: '/reports',
      name: 'reports',
      component: Reports
    },
    {
      // Редирект со старой системы
      path: '/timesheet',
      redirect: { name: 'reports' }
    },
    {
      path: '/report/:id',
      name: 'report',
      component: Report
    },
    {
      path: '/manage_reports',
      name: 'manage_reports',
      component: GIPReports
    },
    {
      // Редирект со старой системы
      path: '/manage',
      redirect: { name: 'manage_reports' }
    },
    {
      path: '/manage_report/:id',
      name: 'manage_report',
      component: GIPReport
    },
    {
      path: '/coefficients',
      name: 'coefficients',
      component: Coefficients
    },
    {
      path: '/bonuses',
      name: 'bonuses',
      component: Bonuses
    },
    {
      path: '/projects',
      name: 'projects',
      component: Projects
    },
    {
      path: '/absences',
      name: 'absences',
      component: Absences
    },
    {
      path: '/stats',
      name: 'stats',
      component: Stats
    },
    {
      path: '/salary',
      name: 'salary',
      component: Salary
    },
    {
      path: '/my_salary',
      name: 'my_salary',
      component: UserSalary
    },
    {
      path: '/replace_user',
      name: 'replace_user',
      component: ReplaceUser
    },
    {
      path: '/orders',
      name: 'orders',
      component: Orders
    },
    {
      path: '/help',
      name: 'help',
      component: Help
    },
    {
      path: '/fillout',
      name: 'fillout',
      component: Fillout
    },
    {
      path: '/storage',
      name: 'storage',
      component: Storage
    },
    {
      path: '/good_kinds',
      name: 'good_kinds',
      component: GoodKinds
    },
    {
      path: '/project_analysis',
      name: 'project_analysis',
      component: ProjectAnalysis
    },
    {
      path: '/project_pies/:type',
      name: 'project_pies',
      component: ProjectPies
    },
    {
      path: '/manufacturers',
      name: 'manufacturers',
      component: Manufacturers
    },
    {
      path: '/b7_export',
      name: 'b7_export',
      component: B7Export
    },
    {
      path: '/tasks',
      name: 'tasks',
      component: Tasks
    },
    {
      path: '/project_state_change',
      name: 'ProjectStateChange',
      component: ProjectStateChange
    },
    {
      path: '/registry_collisions_state_projects',
      name: 'registry_collisions_state_projects',
      component: RegistryCollisionsStateProjects
    },
    {
      path: '/specification',
      name: 'specification',
      component: Specification
    },
    {
      path: '/specification/:id',
      name: 'specificationsPositions',
      component: SpecificationsPositions
    },
    {
      path: '/clients',
      name: 'clients',
      component: Clients
    },
    {
      path: '/contacts',
      name: 'contacts',
      component: Contacts
    },
    {
      path: '/client_history',
      name: 'clientHistory',
      component: ClientHistory
    },
    {
      path: '/my_notifications',
      name: 'my_notifications',
      component: MyNotifications
    },
    {
      path: '/financial_info',
      name: 'financial_info',
      component: FinancialInfo
    },
    {
      path: '/financial_info/history',
      name: 'financial_info_history',
      component: FinancialInfoHistory
    },
    {
      path: '/position_bind',
      name: 'position_bind',
      component: PositionBind
    },
    {
      path: '/salary_payment',
      name: 'salary_payment',
      component: SalaryPayment
    },
    {
      path: '/accruals',
      name: 'accruals',
      component: Accruals
    },
    {
      path: '/buy_application',
      name: 'buy_application',
      component: BuyApplication
    },
    {
      path: '/logistic_request/:id',
      name: 'logistic_request',
      component: LogisticsRequest
    },
    {
      path: '/transfer_requests_list',
      name: 'transfer_requests_list',
      component: TransferRequestsList
    },
    {
      path: '/logistic_delivery',
      name: 'logistic_delivery',
      component: LogisticDelivery
    },
    {
      path: '/transfer_request/:id',
      name: 'transfer_request',
      component: TransferRequest
    },
    // Путь к странице 404 - сюда попадает все то, для чего не совпал ни один из предыдущих путей
    // Должен всегда быть самым последним чтобы работать
    {
      path: '*',
      name: 'page404',
      component: Page404
    }
  ]
})

router.beforeEach((to, from, next) => {
  if (to.path === '/admin/' || to.path === '/download/') {
    // Редиректим жестко, чтобы не сработали хуки роутера js
    const production = process.env.NODE_ENV === 'production'
    if (production) {
      window.location = to.fullPath
    } else {
      window.location = 'http://localhost:8000' + to.fullPath
    }
    return
  }
  if (to.path === '/logout') {
    auth.logout().then(loggedOut => {
      if (loggedOut) {
        apolloClient.resetStore()
      }
      window.location = '/login'
    })
    return
  }
  auth.loggedIn().then(loggedIn => {
    if (to.path === '/login' && loggedIn) {
      next({name: 'default'})
    } else if (to.path !== '/login' && !loggedIn) {
      next({
        path: '/login',
        query: {redirect: to.fullPath}
      })
    } else {
      next()
    }
  })
})

export default router
