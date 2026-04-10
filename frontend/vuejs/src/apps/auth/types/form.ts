export interface RegisterFormValues {
  username?: string;
  email?: string;
  password?: string;
  agreeToTerms?: boolean;
  [key: string]: unknown;
}

export interface PasswordRequirementsRef {
  isValid: boolean;
}

export interface LoginFormValues {
  username?: string;
  password?: string;
  [key: string]: unknown;
}
