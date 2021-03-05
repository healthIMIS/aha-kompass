import HomePage from '../pages/home.f7.html';

import IncidencePage from '../pages/incidence.f7.html';
import DetailPage from '../pages/details.f7.html';
import SearchPage from '../pages/search.f7.html';

import PrivacyPage from '../pages/privacy.f7.html';
import ImprintPage from '../pages/imprint.f7.html';
import AboutPage from '../pages/about.f7.html';
import SteigerPage from '../pages/steiger.f7.html';
import SettingsPage from '../pages/settings.f7.html';

import NotFoundPage from '../pages/404.f7.html';

var routes = [
  {
    path: '/privacy',
    popup: {
      component: PrivacyPage,
    },
  },
  {
    path: '/imprint',
    popup: {
      component: ImprintPage,
    },
  },
  {
    path: '/about',
    popup: {
      component: AboutPage,
    },
  },
  {
    path: '/steiger',
    popup: {
      component: SteigerPage,
    },
  },
  {
    path: '/incidence',
    popup: {
      component: IncidencePage,
    },
  },
  {
    path: '/details',
    popup: {
      component: DetailPage,
    },
  },
  {
    path: '/search',
    popup: {
      component: SearchPage,
    },
  },
  {
    path: '/settings',
    popup: {
      component: SettingsPage,
    },
  },
  {
    path: '/:id?',
    component: HomePage,
  },
  {
    path: '(.*)',
    component: NotFoundPage,
  },
];

export default routes;
