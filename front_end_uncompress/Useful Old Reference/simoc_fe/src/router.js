import Vue from "vue";
import Router from "vue-router";

import {Entry,Configuration,Menu,Dashboard} from './views'
import {Login,Welcome,MainMenu} from './components/entry'
//import {MainMenu,ConfigurationMenu} from './components/mainmenu'

Vue.use(Router);

export default new Router({
  mode: "history",
  base: process.env.BASE_URL,
  routes: [
    {
      path: "/",
      name: "initial",
      component: Entry,

      children:[
        {
          path:'/',
          component: Welcome
        },
        {
          path:'entry',
          name:'entry',
          component:Login
        },
        {
          path:'menu',
          name:'menu',
          component:MainMenu
        }
      ]
    },
    {
      path:"/configurationsession",
      name:"configurationsession",
      component:Configuration,
      props: true,
    },

    {
      path:"/dashboard",
      name:"dashboard",
      component:Dashboard,
    }

    
    /*{
      path: "/about",
      name: "about",
      // route level code-splitting
      // this generates a separate chunk (about.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () =>
        import(webpackChunkName: "about" "./views/About.vue")
    }*/
  ]
});
