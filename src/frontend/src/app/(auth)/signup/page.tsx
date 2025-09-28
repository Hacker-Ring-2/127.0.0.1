// SignupPage.tsx
'use client';

import React, { useState } from 'react';
import { useForm, SubmitHandler } from 'react-hook-form';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { toast } from 'sonner';
import { Loader, Check, X, EyeOff, Eye } from 'lucide-react';
import { cn } from '@/lib/utils';
import ApiServices from '@/services/ApiServices';
import { SignupFormData } from '@/types/auth-types';
import Cookies from 'js-cookie';
import OTPDialog, { IRegisterationData } from './components/OTPDialog';
import Image from 'next/image';

const SignupPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);

  const router = useRouter();

  const {
    register,
    handleSubmit,
    watch,
    reset,
    formState: { errors },
  } = useForm<SignupFormData>();

  // watch password and confirm
  const password = watch('password', '');
  const confirm = watch('confirmPassword', '');

  const [otp, setOtp] = useState('');

  const [openOTPDialog, setOpenOTPDialog] = useState(false);
  const [registerationData, setRegisterationData] = useState<IRegisterationData | null>(null);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  // has the user started typing a password?
  const isTouched = password.length > 0;
  // has the user started typing confirmation?
  const confirmTouched = confirm.length > 0;

  // password rules
  const rules = {
    length: password.length >= 8,
    upper: /[A-Z]/.test(password),
    lower: /[a-z]/.test(password),
    number: /[0-9]/.test(password),
    special: /[@$!%*?&]/.test(password),
    match: confirm.length > 0 && password === confirm,
  };

  // all password rules except match (we can include match too if desired)
  const allValid = Object.values(rules).every(Boolean);

  // Add this helper function inside your SignupPage component

  const handleSuccessfulAuth = async (token: string) => {
    try {
      // 1. Set the cookie so the next API call is authenticated
      Cookies.set('access_token', token, { path: '/' });

      // 2. Check if the user is new
      const isNew = await ApiServices.isNewUser();

      toast.success('Authentication Successful');

      // 3. Conditionally redirect
      if (isNew) {
        router.push('/onboarding');
      } else {
        router.push('/'); // Or your main app page for existing users
      }
    } catch {
      toast.error('Could not verify user status. Please try again.');
    } finally {
      // Reset all loading states
      setIsLoading(false);
    }
  };

  const onSubmit: SubmitHandler<SignupFormData> = async (data) => {
    setIsLoading(true);
    try {
      // const rawPhone = `${selectedCountry?.dial_code}${data.phone.replace(/^0+/, '')}`;
      // const phoneNumber = parsePhoneNumberFromString(rawPhone);
      // const formattedPhone = phoneNumber ? phoneNumber.number : rawPhone;
      const { fullName, email, password } = data;

      setRegisterationData({ fullName, email, password });
      const response = await ApiServices.signup(
        fullName,
        email,
        // formattedPhone,
        password
      );
      setOpenOTPDialog(true);
      setOtp(response?.OTP || '')
    } catch (error: unknown) {
      const err = error as { response?: { data?: { detail?: string } } };
      toast.error(err?.response?.data?.detail || 'Something went wrong. Please try again.');
    } finally {
      setIsLoading(false);
      reset();
    }
  };


  return (
    <div className="min-h-screen h-auto w-full flex flex-col justify-center py-12 sm:px-6 px-2 lg:px-8 overflow-auto bg-[var(--primary-main-bg)]">
      <div className="sm:mx-auto sm:w-full sm:max-w-md flex justify-center items-center">
        <h1 className="text-center sm:text-[2rem] text-[1.5rem] font-normal align-self-stretch">
          <Image
            src="/images/login_logo.svg" // This path must be correct
            width={231}
            height={48}
            alt="logo"
          />
        </h1>
      </div>

      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="sm:py-10 py-4 px-2 sm:px-10">
         
          {/* -----------Signup Form------------ */}
          <form
            noValidate
            autoComplete="off"
            className="space-y-4"
            onSubmit={handleSubmit(onSubmit)}
          >
            {/* Full Name */}
            <div>
              <input
                type="text"
                placeholder="Full Name"
                className={cn(
                  'block w-full px-3 py-3 bg-[var(--primary-chart-bg)] border  rounded-md shadow-sm placeholder-neutral-150 focus:outline-none focus:ring-2 focus:ring-[#4B9770] sm:text-sm transitiona-ll duration-200',
                  errors.fullName ? 'border-red-500 focus:ring-red-500' : 'border-primary-100'
                )}
                {...register('fullName', {
                  required: 'Full name is required',
                  minLength: {
                    value: 2,
                    message: 'Name must be at least 2 characters',
                  },
                })}
              />
              {errors.fullName && (
                <p className="mt-1 text-sm text-red-600">{errors.fullName.message}</p>
              )}
            </div>

            {/* Email */}
            <div>
              <input
                type="email"
                placeholder="Email"
                className={cn(
                  'block w-full px-3 py-3 bg-[var(--primary-chart-bg)] border rounded-md shadow-sm placeholder-neutral-150 focus:outline-none focus:ring-2 focus:ring-[#4B9770] sm:text-sm transition-all duration-200',
                  errors.email ? 'border-red-500 focus:ring-red-500' : 'border-primary-100'
                )}
                {...register('email', {
                  required: 'Email is required',
                  pattern: {
                    value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                    message: 'Invalid email address',
                  },
                })}
              />
              {errors.email && <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>}
            </div>

            
            {/* Password */}
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                placeholder="Password"
                className={cn(
                  'block w-full px-3 py-3 pr-10 bg-[var(--primary-chart-bg)] border  rounded-md shadow-sm placeholder-neutral-150 focus:outline-none focus:ring-2 focus:ring-[#4B9770] sm:text-sm transition-all duration-200',
                  errors.password ? 'border-red-500 focus:ring-red-500' : 'border-primary-100'
                )}
                {...register('password', { required: 'Password is required' })}
              />
              <button
                type="button"
                onClick={() => setShowPassword((prev) => !prev)}
                className="absolute inset-y-0 right-3 flex items-center"
              >
                {!showPassword ? (
                  <EyeOff className="w-5 h-5 text-neutral-500" />
                ) : (
                  <Eye className="w-5 h-5 text-neutral-500" />
                )}
              </button>
              {errors.password && (
                <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
              )}
            </div>

            {/* Confirm Password Field */}
            <div className="relative">
              <input
                type={showConfirmPassword ? 'text' : 'password'}
                placeholder="Confirm Password"
                className={cn(
                  'block w-full px-3 py-3 pr-10 bg-[var(--primary-chart-bg)] border  rounded-md shadow-sm placeholder-neutral-150 focus:outline-none focus:ring-2 focus:ring-[#4B9770] sm:text-sm transition-all duration-200',
                  errors.confirmPassword
                    ? 'border-red-500 focus:ring-red-500'
                    : 'border-primary-100'
                )}
                {...register('confirmPassword', { required: 'Please confirm your password' })}
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword((prev) => !prev)}
                className="absolute inset-y-0 right-3 flex items-center"
              >
                {!showConfirmPassword ? (
                  <EyeOff className="w-5 h-5 text-neutral-500" />
                ) : (
                  <Eye className="w-5 h-5 text-neutral-500" />
                )}
              </button>
            </div>

            {/* Live checklist */}
            <ul className="mt-3 space-y-1 text-sm">
              <li className="flex items-center">
                {rules.length ? (
                  <Check
                    className={cn('w-4 h-4', !isTouched ? 'text-neutral-500' : 'text-green-500')}
                  />
                ) : (
                  <X className={cn('w-4 h-4', !isTouched ? 'text-neutral-500' : 'text-red-500')} />
                )}
                <span
                  className={cn(
                    'ml-2 text-xs font-normal',
                    !isTouched
                      ? 'text-neutral-500'
                      : rules.length
                        ? 'text-green-600'
                        : 'text-red-500'
                  )}
                >
                  Be at least 8 characters long.
                </span>
              </li>

              <li className="flex items-center">
                {rules.upper ? (
                  <Check
                    className={cn('w-4 h-4', !isTouched ? 'text-neutral-500' : 'text-green-500')}
                  />
                ) : (
                  <X className={cn('w-4 h-4', !isTouched ? 'text-neutral-500' : 'text-red-500')} />
                )}
                <span
                  className={cn(
                    'ml-2 text-xs font-normal',
                    !isTouched
                      ? 'text-neutral-500'
                      : rules.upper
                        ? 'text-green-600'
                        : 'text-red-500'
                  )}
                >
                  Include at least one uppercase letter (A-Z).
                </span>
              </li>

              <li className="flex items-center">
                {rules.lower ? (
                  <Check
                    className={cn('w-4 h-4', !isTouched ? 'text-neutral-500' : 'text-green-500')}
                  />
                ) : (
                  <X className={cn('w-4 h-4', !isTouched ? 'text-neutral-500' : 'text-red-500')} />
                )}
                <span
                  className={cn(
                    'ml-2 text-xs font-normal',
                    !isTouched
                      ? 'text-neutral-500'
                      : rules.lower
                        ? 'text-green-600'
                        : 'text-red-500'
                  )}
                >
                  Include at least one lowercase letter (a-z).
                </span>
              </li>

              <li className="flex items-center">
                {rules.number ? (
                  <Check
                    className={cn('w-4 h-4', !isTouched ? 'text-neutral-500' : 'text-green-500')}
                  />
                ) : (
                  <X className={cn('w-4 h-4', !isTouched ? 'text-neutral-500' : 'text-red-500')} />
                )}
                <span
                  className={cn(
                    'ml-2 text-xs font-normal',
                    !isTouched
                      ? 'text-neutral-500'
                      : rules.number
                        ? 'text-green-600'
                        : 'text-red-500'
                  )}
                >
                  Include at least one number (0-9).
                </span>
              </li>

              <li className="flex items-center">
                {rules.special ? (
                  <Check
                    className={cn('w-4 h-4', !isTouched ? 'text-neutral-500' : 'text-green-500')}
                  />
                ) : (
                  <X className={cn('w-4 h-4', !isTouched ? 'text-neutral-500' : 'text-red-500')} />
                )}
                <span
                  className={cn(
                    'ml-2 text-xs font-normal',
                    !isTouched
                      ? 'text-neutral-500'
                      : rules.special
                        ? 'text-green-600'
                        : 'text-red-500'
                  )}
                >
                  Include at least one special character (e.g. !@#$%).
                </span>
              </li>

              <li className="flex items-center">
                {rules.match ? (
                  <Check
                    className={cn(
                      'w-4 h-4',
                      !confirmTouched ? 'text-neutral-500' : 'text-green-500'
                    )}
                  />
                ) : (
                  <X
                    className={cn('w-4 h-4', !confirmTouched ? 'text-neutral-500' : 'text-red-500')}
                  />
                )}
                <span
                  className={cn(
                    'ml-2 text-xs font-normal',
                    !confirmTouched
                      ? 'text-neutral-500'
                      : rules.match
                        ? 'text-green-600'
                        : 'text-red-500'
                  )}
                >
                  Passwords match.
                </span>
              </li>
            </ul>

            {/* Submit */}
            <div>
              <button
                type="submit"
                disabled={!allValid || !rules.match || isLoading}
                className={cn(
                  'w-full flex justify-center items-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-[#4B9770] hover:bg-[#408160] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#4B9770] disabled:opacity-50 disabled:cursor-not-allowed'
                )}
              >
                {isLoading && <Loader className="w-5 h-5 mr-2 animate-spin" />}
                Continue
              </button>
            </div>
          </form>

          {/* ----------LogIn Link--------- */}
          <div className="mt-5 text-center text-sm">
            <p className="text-neutral-150">
              Already have an account?{' '}
              <Link href="/login" className="font-medium text-[#4B9770] hover:text-[#408160]">
                Log in
              </Link>
            </p>
          </div>
        </div>
      </div>

      {registerationData &&otp&& (
        <OTPDialog
          open={openOTPDialog}
          registerationData={registerationData}
          onOpenChange={setOpenOTPDialog}
          onVerificationSuccess={(token) => handleSuccessfulAuth(token)}
          OTP={otp}
        />
      )}
    </div>
  );
};

export default SignupPage;
