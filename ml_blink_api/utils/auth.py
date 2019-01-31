import bcrypt

def encrypt_user_password(user):
  '''
  Given a user, augment its attributes with a salt and a password (hashed)
  with that salt
  '''
  user['salt'] = bcrypt.gensalt()
  password = user.get('password')
  user['password'] = bcrypt.hashpw(password, user.get('salt'))
  return user


def password_matches(user, password):
  '''
  Return true if a user password matches the argument `password`, false otherwise
  '''
  return bcrypt.hashpw(password, user.get('salt')) == user.get('password')
