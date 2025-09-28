import axios from 'axios';
import { API_ENDPOINTS } from './endpoints';
import { axiosInstance } from './axiosInstance';
import { IFinanceData } from '@/components/charts/FinanaceChart';
const BASE_URL = process.env.NEXT_PUBLIC_BASE_URL || '';

interface RelatedQueriesRequest {
  message_id: string;
  chart_session_id: string;
  context_data: IFinanceData[];
  name: string;
  ticker: string;
  exchange: string;
}

// API Response interfaces
interface LoginResponse {
  access_token: string;
  token_type: string;
  user_id?: string;
}

interface SignupResponse {
  success: boolean;
  message: string;
  OTP?: string;
  user_id?: string;
}



interface GenericApiResponse {
  data?: {
    data: unknown;
    has_more?: boolean;
  };
  [key: string]: unknown;
}

interface OnboardingData {
  [key: string]: unknown;
}
class ApiServices {
  async login(username: string, password: string): Promise<LoginResponse> {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    const response = await axios.post(API_ENDPOINTS.LOGIN, formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  }

  async isNewUser(): Promise<boolean> {
    try {
      const response = await axiosInstance.get<boolean>(API_ENDPOINTS.IS_NEW_USER);
      return response.data;
    } catch (error) {
      console.error('Error checking if user is new:', error);
      throw error;
    }
  }

  async signup(
    fullName: string,
    email: string,
    // phone: string,
    password: string
  ): Promise<SignupResponse> {
    const response = await axios.post(
      API_ENDPOINTS.SIGNUP,
      {
        full_name: fullName,
        email,
        // phone,
        password,
      },
      {
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );
    return response.data;
  }

  async getSessionHistory(
    page?: number,
    limit?: number,
    signal?: AbortSignal,
    keyword?: string
  ): Promise<GenericApiResponse> {
    const params: Record<string, string | number> = { keyword: '' };

    if (page !== undefined) params.page = page;
    if (limit !== undefined) params.limit = limit;
    if (keyword !== undefined) params.keyword = keyword;

    const response = await axiosInstance.get(
      `${API_ENDPOINTS.SESSION_HISTORY}?keyword=${params.keyword}&page=${params.page}&limit=${params.limit}`,
      {
        signal,
      }
    );

    return response.data;
  }

  async getSessionTitle(
    input: string,
    signal: AbortSignal,
    page?: number,
    limit?: number
  ): Promise<GenericApiResponse> {
    const params: Record<string, string | number> = { input: '' };

    if (page !== undefined) params.page = page;
    if (limit !== undefined) params.limit = limit;
    if (input !== undefined) params.input = input;
    const response = await axiosInstance.get(
      `${API_ENDPOINTS.SEARCH_THREAD}/search?keyword=${input}&page=${params.page}&limit=${params.limit}`,
      {
        signal,
      }
    );
    return response.data;
  }

  async updatePublicSession(sessionId: string, access = 'public') {
    const response = await axiosInstance.put(API_ENDPOINTS.UPDATE_SESSION_ACCESS, {
      session_id: sessionId,
      access_level: access,
    });

    return response.data;
  }

  async updateMessageAccess(sessionId: string, messageId: string, access = 'public') {
    const response = await axiosInstance.put(API_ENDPOINTS.UPDATE_MESSAGE_ACCESS, {
      session_id: sessionId,
      message_id: messageId,
      access_level: access,
    });

    return response.data;
  }

  async fetchRelatedQueries(payload: RelatedQueriesRequest) {
    try {
      const response = await axiosInstance.post(
        `/related-queries?message_id=${payload.message_id}&chart_session_id=${payload.chart_session_id}`,
        {
          context_data: payload.context_data,
          exchange: payload.exchange,
          ticker: payload.ticker,
          name: payload.name,
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error fetching related queries:', error);
      throw error;
    }
  }

  async fetchChatData(chatId: string) {
    try {
      const response = await axiosInstance.get(`/chat/${chatId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching chat data:', error);
      throw error;
    }
  }

  async connectToChatBot({
    message_id,
    chart_session_id,
    session_id,
    user_input,
    context_data,
    ticker,
    exchange,
    name,
  }: {
    message_id: string;
    chart_session_id: string;
    session_id: string;
    user_input: string;
    context_data: IFinanceData[];
    ticker: string;
    exchange: string;
    name: string;
  }) {
    try {
      const response = await axiosInstance.post(
        `/chat_bot`,
        {
          context_data,
          ticker,
          exchange,
          name,
        },
        {
          params: {
            user_input,
            session_id,
            message_id,
            chat_session_id: chart_session_id,
          },
        }
      );

      return response.data;
    } catch (error) {
      console.error('Error connecting to chatbot:', error);
      throw error;
    }
  }

  async getSharedCoversationData(sessionId: string) {
    const response = await axios.get(
      `${BASE_URL}${API_ENDPOINTS.SHARED_CONVERSATION}/${sessionId}`
    );
    return response.data;
  }

  async getSharedMessageData(messageId: string) {
    const response = await axios.get(`${BASE_URL}${API_ENDPOINTS.SHARED_MESSAGE}/${messageId}`);
    return response.data;
  }

  async exportResponse(messageId: string, format: string) {
    try {
      const response = await axiosInstance.post(API_ENDPOINTS.EXPORT_RESPONSE, {
        message_id: messageId,
        format,
      });
      return response.data;
    } catch (error) {
      console.error('error in exprt response api', error);
      throw error;
    }
  }

  async uploadFiles(file: File) {
    const formData = new FormData();
    formData.append('file', file); // ✅ Must match the 'file' field in curl

    const response = await axiosInstance.post(
      `${API_ENDPOINTS.UPLOAD_FILE}`, //
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data', // optional — axios sets this automatically when using FormData
        },
      }
    );

    return response.data;
  }

  async handlePreviewFile(fileId: string): Promise<string> {
    try {
      const response = await axiosInstance.get(`${API_ENDPOINTS.PREVIEW_FILE}/${fileId}`, {
        responseType: 'blob', // Ensure the response is treated as a blob
      });
      // Create a URL for the blob
      const blob = response.data; // already a valid Blob with correct MIME type
      const url = URL.createObjectURL(blob);
      return url;
    } catch (error) {
      console.error('Error fetching file preview:', error);
      throw error;
    }
  }

  async handleSessionDelete(sessionId: string) {
    try {
      const response = await axiosInstance.delete(`${API_ENDPOINTS.DELETE_SESSION}/${sessionId}`);
      return response.data;
    } catch (error) {
      console.error('Error deleting session:', error);
      throw error;
    }
  }

  async handleOnboardingQuestion(onBoardingData: OnboardingData) {
    try {
      const response = await axiosInstance.post(`${API_ENDPOINTS.USER_ONBOARDING}`, {
        ...onBoardingData,
      });
      return response.data;
    } catch (error) {
      console.error('Error in onboarding', error);
      throw error;
    }
  }

  async handleStopGeneratingResponse(sessionId: string, messageId: string): Promise<GenericApiResponse> {
    try {
      const response = await axiosInstance.post(
        `${API_ENDPOINTS.STOP_GENERATING_RESPONSE}?session_id=${sessionId}&message_id=${messageId}`
      );
      return response.data;
    } catch (error) {
      console.error('Error stopping response generation:', error);
      throw error;
    }
  }

  async getStockPredictionData(
    ticker: string,
    symbol: string,
    messageId: string,
    companyName: string
  ): Promise<GenericApiResponse> {
    const data = {
      ticker: ticker,
      exchange_symbol: symbol,
      message_id: messageId,
      company_name: companyName,
    };
    try {
      const response = await axiosInstance.post(`${API_ENDPOINTS.STOCK_PREDICTION}`, data);
      return response.data;
    } catch (error) {
      console.error('Error fetching stock prediction:', error);
      throw error;
    }
  }

  async handleAccountDelete(): Promise<GenericApiResponse> {
    try {
      const response = await axiosInstance.delete(`user`);
      return response.data;
    } catch (error) {
      console.error('Error deleting account:', error);
      throw error;
    }
  }

  async handleFetchStockSession(sessionId: string): Promise<GenericApiResponse> {
    try {
      const response = await axiosInstance.get(`chat/session/${sessionId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching stock session:', error);
      throw error;
    }
  }

  async getUserDetails(): Promise<GenericApiResponse> {
    try {
      const response = await axiosInstance.get(`${API_ENDPOINTS.GET_USER_DETAILS}`);
      console.log(response);
      return response.data;
    } catch (error) {
      console.log(error);
      throw error;
    }
  }

  async updateCanvasMarkdown(
    document_id: string,
    version_number: number,
    full_content: string
  ): Promise<GenericApiResponse> {
    try {
      const response = await axiosInstance.post(`${API_ENDPOINTS.CANVAS_UPDATE_MARKDOWN}`, {
        document_id,
        version_number,
        full_content,
      });
      return response.data;
    } catch (error: unknown) {
      console.error(error);
      throw error;
    }
  }

  async downloadCanvasData(
    document_id: string,
    version_number: number,
    format: string
  ): Promise<GenericApiResponse> {
    try {
      const response = await axiosInstance.post(`${API_ENDPOINTS.DOWNLOAD_CANVAS_DATA}`, {
        document_id,
        version_number,
        format,
      });
      return response.data;
    } catch (error: unknown) {
      console.error(error);
      throw error;
    }
  }

  async getCanvasVersion(document_id: string, version_number: number): Promise<GenericApiResponse> {
    try {
      const response = await axiosInstance.get(
        `${API_ENDPOINTS.GET_CANVAS_VERSION}/${document_id}/version/${version_number}`
      );
      return response.data;
    } catch (error: unknown) {
      console.error('Error fetching canvas version:', error);
      throw error;
    }
  }

  async makeCanvasVersionLatest(
    document_id: string,
    version_number: number,
    session_id: string,
    message_id: string
  ): Promise<GenericApiResponse> {
    try {
      const response = await axiosInstance.post(
        `${API_ENDPOINTS.CANVAS_MAKE_VERSION_LATEST}/${document_id}/make-version-latest/${version_number}`,
        {
          session_id,
          message_id,
        }
      );
      return response.data;
    } catch (error: unknown) {
      console.error('Error making canvas version latest:', error);
      throw error;
    }
  }

  async updateCurrentVersionOfCanvasData(
    docId: string,
    version_number: number,
    session_id: string,
    message_id: string
  ): Promise<GenericApiResponse> {
    try {
      const apiUrl = API_ENDPOINTS.CANVAS_MAKE_VERSION_LATEST_WITH_ID(docId, version_number);
      const response = await axiosInstance.post(apiUrl, { session_id, message_id });
      return response.data;
    } catch (error: unknown) {
      console.error('Error updating current version of canvas data:', error);
      throw error;
    }
  }
}

const apiServicesInstance = new ApiServices();
export default apiServicesInstance;
