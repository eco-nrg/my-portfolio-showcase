export default async function ({ route, redirect, $cookies }) {
  const cookies = $cookies.get('auth')

  if (cookies && cookies !== '') {
    if (route.path === '/') {
      redirect('/profile');
    }
  } else {
    if (route.path === '/spaces' && route.query?.id) {
      redirect(`/?id=${route.query.id}`);
    }else if (route.path !== '/') {
      redirect('/');
    }
  }
}