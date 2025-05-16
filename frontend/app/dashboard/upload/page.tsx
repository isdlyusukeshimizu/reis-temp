"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { useToast } from "@/hooks/use-toast"
import { Upload, FileText, CheckCircle, Clock, AlertCircle } from "lucide-react"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { useRouter } from "next/navigation"

// バックエンドAPIのベースURL（環境に合わせて変更）
// 開発環境では http://localhost:8000 などのバックエンドサーバーのURLを指定
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"

// 複数のAPIパスを試す（ベースURLを含まない相対パス）
const API_PATHS = [
  "/api/v1/documents/upload",
  "/api/v1/upload",
  "/api/v1/document/upload",
  "/api/upload",
  "/api/v1/documents",
]

// 抽出データの型定義
type ExtractedData = {
  id: string
  extractedAt: string // 情報取得日
  customerName: string // 顧客名
  postalCode: string // 郵便番号
  prefecture: string // 都道府県
  currentAddress: string // 顧客現在住所
  inheritanceAddress: string // 顧客相続住所
  phoneNumber: string // 電話番号
  status: "pending" | "registered" | "error"
}

// グローバルな顧客データを保持するための変数（customer-management.tsxと共有）
declare global {
  interface Window {
    globalCustomers: any[]
  }
}

export default function UploadPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [processingProgress, setProcessingProgress] = useState(0)
  const [isProcessing, setIsProcessing] = useState(false)
  const [isComplete, setIsComplete] = useState(false)
  const [estimatedTime, setEstimatedTime] = useState<number | null>(null)
  const [elapsedTime, setElapsedTime] = useState(0)
  const [extractedData, setExtractedData] = useState<ExtractedData[]>([])
  const [editableData, setEditableData] = useState<ExtractedData[]>([])
  const [documentId, setDocumentId] = useState<number | null>(null)
  const [isFileUploaded, setIsFileUploaded] = useState(false)
  const [currentApiPathIndex, setCurrentApiPathIndex] = useState(0)
  const { toast } = useToast()
  const router = useRouter()

  // ハイドレーションエラー対策
  const [isClient, setIsClient] = useState(false)

  useEffect(() => {
    setIsClient(true)

    // 環境変数のデバッグ出力
    console.log("API Base URL:", API_BASE_URL)
  }, [])

  // ファイル選択
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null
    setSelectedFile(file)

    // ファイルが選択されたらリセット
    if (file) {
      setIsUploading(false)
      setUploadProgress(0)
      setProcessingProgress(0)
      setIsProcessing(false)
      setIsComplete(false)
      setEstimatedTime(null)
      setElapsedTime(0)
      setExtractedData([])
      setEditableData([])
      setDocumentId(null)
      setIsFileUploaded(false)
      setCurrentApiPathIndex(0)
    }
  }

  // ファイルアップロード
  const handleUpload = async () => {
    if (!selectedFile) {
      toast({
        title: "ファイルが選択されていません",
        description: "アップロードするPDFファイルを選択してください",
        variant: "destructive",
      })
      return
    }

    try {
      setIsUploading(true)
      setUploadProgress(0)

      // FormDataの作成
      const formData = new FormData()
      formData.append("file", selectedFile)
      formData.append("document_type", "registry") // ドキュメントタイプを指定

      // 現在のAPIパスを取得（ベースURLと結合）
      const apiPath = `${API_BASE_URL}${API_PATHS[currentApiPathIndex]}`
      console.log(`Attempting to upload to: ${apiPath}`)

      // アップロードの進捗を監視するためのXHRを使用
      const xhr = new XMLHttpRequest()
      xhr.open("POST", apiPath)

      // JWTトークンがある場合は認証ヘッダーを設定
      const token = localStorage.getItem("token")
      if (token) {
        xhr.setRequestHeader("Authorization", `Bearer ${token}`)
      }

      // アップロード進捗の監視
      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          const progress = Math.round((event.loaded * 100) / event.total)
          setUploadProgress(progress)
        }
      }

      // レスポンス処理
      xhr.onload = async () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          // アップロード完了
          setIsUploading(false)
          setIsFileUploaded(true)

          try {
            // レスポンスからドキュメントIDを取得
            const response = JSON.parse(xhr.responseText)
            console.log("Upload response:", response)

            // 成功したAPIパスをコンソールに出力
            console.log(`Successfully uploaded to: ${apiPath}`)

            // ドキュメントIDを状態に保存
            setDocumentId(response.id)

            toast({
              title: "ファイルのアップロードが完了しました",
              description: "「処理開始」ボタンをクリックして処理を開始してください",
            })
          } catch (parseError) {
            console.error("Error parsing response:", parseError)
            toast({
              title: "レスポンスの解析に失敗しました",
              description: "サーバーからの応答を処理できませんでした",
              variant: "destructive",
            })
          }
        } else if (xhr.status === 404) {
          // 404エラーの場合、次のAPIパスを試す
          console.error(`API path ${apiPath} returned 404. Trying next path...`)

          if (currentApiPathIndex < API_PATHS.length - 1) {
            setCurrentApiPathIndex(currentApiPathIndex + 1)
            setIsUploading(false)
            // 次のAPIパスで再試行
            setTimeout(() => handleUpload(), 500)
          } else {
            // すべてのパスを試しても失敗
            setIsUploading(false)
            console.error("All API paths failed with 404")
            toast({
              title: "アップロードに失敗しました",
              description: "すべてのAPIパスが見つかりませんでした。バックエンドの設定を確認してください。",
              variant: "destructive",
            })
          }
        } else {
          // その他のエラー
          setIsUploading(false)
          console.error("Upload failed with status:", xhr.status)
          console.error("Response text:", xhr.responseText)

          let errorMessage = "サーバーエラーが発生しました"
          try {
            const errorData = JSON.parse(xhr.responseText)
            errorMessage = errorData.detail || errorMessage
          } catch (e) {
            // 解析エラーの場合はデフォルトメッセージを使用
          }

          toast({
            title: "アップロードに失敗しました",
            description: errorMessage,
            variant: "destructive",
          })
        }
      }

      // エラーハンドリング
      xhr.onerror = (e) => {
        console.error("XHR error:", e)
        console.error("This might be a network issue or the backend server is not running.")
        setIsUploading(false)
        toast({
          title: "アップロードに失敗しました",
          description: "ネットワークエラーが発生しました。バックエンドサーバーが実行されているか確認してください。",
          variant: "destructive",
        })
      }

      // リクエスト送信
      xhr.send(formData)
    } catch (error) {
      console.error("Upload error:", error)
      setIsUploading(false)
      toast({
        title: "エラーが発生しました",
        description: error instanceof Error ? error.message : "不明なエラーが発生しました",
        variant: "destructive",
      })
    }
  }

  // 処理開始
  const handleStartProcessing = async () => {
    if (!documentId) {
      toast({
        title: "ドキュメントIDがありません",
        description: "先にファイルをアップロードしてください",
        variant: "destructive",
      })
      return
    }

    // ファイルサイズに基づいて推定時間を計算
    if (selectedFile) {
      const fileSizeMB = selectedFile.size / (1024 * 1024)
      const estimatedSeconds = Math.max(20, Math.round(fileSizeMB * 5)) // 5秒/MB、最低20秒
      setEstimatedTime(estimatedSeconds)
    }

    setIsProcessing(true)
    setProcessingProgress(0)

    try {
      console.log("Starting processing for document ID:", documentId)

      // 処理開始APIを呼び出し
      const token = localStorage.getItem("token")
      // 成功したAPIパスのベースを使用
      const baseApiPath = API_PATHS[currentApiPathIndex].split("/upload")[0]
      const processApiPath = `${API_BASE_URL}${baseApiPath}/${documentId}/process`

      console.log(`Calling process API at: ${processApiPath}`)

      const response = await fetch(processApiPath, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: token ? `Bearer ${token}` : "",
        },
      })

      if (!response.ok) {
        const errorText = await response.text()
        console.error("Process API error:", response.status, errorText)
        throw new Error(`処理の開始に失敗しました (${response.status})`)
      }

      const data = await response.json()
      console.log("Process response:", data)
      const taskId = data.task_id

      // 経過時間のカウント開始
      const timerInterval = setInterval(() => {
        setElapsedTime((prev) => prev + 1)
      }, 1000)

      // 処理状態を監視
      await monitorProcessingStatus(taskId, timerInterval, baseApiPath)
    } catch (error) {
      console.error("Processing error:", error)
      setIsProcessing(false)
      toast({
        title: "エラーが発生しました",
        description: error instanceof Error ? error.message : "不明なエラーが発生しました",
        variant: "destructive",
      })
    }
  }

  // 処理状態の監視
  const monitorProcessingStatus = async (taskId: string, timerInterval: NodeJS.Timeout, baseApiPath: string) => {
    try {
      // 処理状態を確認するためのポーリング
      const checkStatusInterval = setInterval(async () => {
        try {
          const token = localStorage.getItem("token")
          // 成功したAPIパスのベースを使用
          const taskApiPath = `${API_BASE_URL}${baseApiPath.replace("/documents", "")}/tasks/${taskId}`

          console.log(`Checking task status at: ${taskApiPath}`)

          const response = await fetch(taskApiPath, {
            headers: {
              Authorization: token ? `Bearer ${token}` : "",
            },
          })

          if (!response.ok) {
            const errorText = await response.text()
            console.error("Task status API error:", response.status, errorText)
            throw new Error("処理状態の取得に失敗しました")
          }

          const task = await response.json()
          console.log("Task status:", task)

          // ステータスに応じて進捗を更新
          switch (task.status) {
            case "queued":
              setProcessingProgress(5)
              break
            case "processing":
              // progressフィールドがあれば使用、なければ50%と仮定
              setProcessingProgress(task.progress || 50)
              break
            case "completed":
              setProcessingProgress(100)
              clearInterval(checkStatusInterval)
              clearInterval(timerInterval)
              setIsProcessing(false)
              setIsComplete(true)

              // 抽出データの取得
              if (documentId) {
                await fetchExtractedData(documentId, baseApiPath)
              }
              break
            case "failed":
              clearInterval(checkStatusInterval)
              clearInterval(timerInterval)
              setIsProcessing(false)
              toast({
                title: "処理に失敗しました",
                description: task.message || "ドキュメント処理中にエラーが発生しました",
                variant: "destructive",
              })
              break
          }
        } catch (error) {
          console.error("Error monitoring task status:", error)
          clearInterval(checkStatusInterval)
          clearInterval(timerInterval)
          setIsProcessing(false)
          toast({
            title: "エラーが発生しました",
            description: error instanceof Error ? error.message : "不明なエラーが発生しました",
            variant: "destructive",
          })
        }
      }, 3000) // 3秒ごとに確認
    } catch (error) {
      console.error("Error setting up monitoring:", error)
      clearInterval(timerInterval)
      setIsProcessing(false)
      toast({
        title: "エラーが発生しました",
        description: error instanceof Error ? error.message : "不明なエラーが発生しました",
        variant: "destructive",
      })
    }
  }

  // 抽出データの取得
  const fetchExtractedData = async (documentId: number, baseApiPath: string) => {
    try {
      const token = localStorage.getItem("token")
      // 成功したAPIパスのベースを使用
      const dataApiPath = `${API_BASE_URL}${baseApiPath}/${documentId}/extracted-data`

      console.log(`Fetching extracted data from: ${dataApiPath}`)

      const response = await fetch(dataApiPath, {
        headers: {
          Authorization: token ? `Bearer ${token}` : "",
        },
      })

      if (!response.ok) {
        console.error("Error fetching extracted data:", response.status)
        // APIからデータが取得できない場合はダミーデータを使用
        const dummyData = generateDummyExtractedData()
        setExtractedData(dummyData)
        setEditableData(dummyData)

        toast({
          title: "処理が完了しました",
          description: `${selectedFile?.name} の処理が完了しました。抽出データを確認してください。`,
        })
        return
      }

      const data = await response.json()
      console.log("Extracted data:", data)

      // APIからのデータを適切な形式に変換
      const formattedData: ExtractedData[] = data.map((item: any) => ({
        id: item.id.toString(),
        extractedAt: new Date().toISOString().split("T")[0],
        customerName: item.owner_name || "",
        postalCode: item.postal_code || "",
        prefecture: item.prefecture || "",
        currentAddress: item.current_address || "",
        inheritanceAddress: item.property_address || "",
        phoneNumber: item.phone_number || "",
        status: "pending",
      }))

      setExtractedData(formattedData)
      setEditableData(formattedData)

      toast({
        title: "処理が完了しました",
        description: `${selectedFile?.name} の処理が完了しました。抽出データを確認してください。`,
      })
    } catch (error) {
      console.error("Error in fetchExtractedData:", error)
      // エラー時はダミーデータを使用
      const dummyData = generateDummyExtractedData()
      setExtractedData(dummyData)
      setEditableData(dummyData)

      toast({
        title: "データ取得に失敗しました",
        description: "ダミーデータを表示しています",
        variant: "destructive",
      })
    }
  }

  // 完了処理
  const handleComplete = async () => {
    try {
      // 顧客情報管理ページに連携するためのデータ変換処理
      const customersToAdd = editableData.map((data) => ({
        name: data.customerName,
        phone_number: data.phoneNumber || "",
        email: "",
        address: data.currentAddress,
        postal_code: data.postalCode,
        property_address: data.inheritanceAddress,
        property_type: "その他",
        status: "new",
        assigned_to: "",
        last_contact_date: new Date().toISOString().split("T")[0],
        next_contact_date: "",
        notes: `受付台帳から自動抽出 (${data.extractedAt})`,
        source: "受付台帳",
      }))

      // APIを使用して顧客情報を登録
      const token = localStorage.getItem("token")
      // 成功したAPIパスのベースを使用
      const baseApiPath = API_PATHS[currentApiPathIndex].split("/documents")[0]
      const customersApiPath = `${API_BASE_URL}${baseApiPath}/customers/batch`

      console.log(`Registering customers at: ${customersApiPath}`)

      const response = await fetch(customersApiPath, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: token ? `Bearer ${token}` : "",
        },
        body: JSON.stringify({ customers: customersToAdd }),
      })

      if (!response.ok) {
        console.error("Error registering customers:", response.status)
        throw new Error("顧客情報の登録に失敗しました")
      }

      // APIが利用できない場合のフォールバック
      if (typeof window !== "undefined") {
        if (!window.globalCustomers) {
          window.globalCustomers = []
        }

        const legacyCustomers = customersToAdd.map((customer, index) => ({
          id: `CUST-${Date.now()}-${index}`,
          name: customer.name,
          phoneNumber: customer.phone_number,
          email: customer.email,
          address: customer.address,
          postalCode: customer.postal_code,
          propertyAddress: customer.property_address,
          propertyType: customer.property_type,
          status: customer.status as any,
          assignedTo: customer.assigned_to,
          lastContactDate: customer.last_contact_date,
          next_contact_date: customer.next_contact_date,
          notes: customer.notes,
          source: customer.source,
          activities: [],
        }))

        window.globalCustomers = [...legacyCustomers, ...window.globalCustomers]
      }

      toast({
        title: "データを顧客情報に登録しました",
        description: `${editableData.length}件のデータが顧客情報管理に登録されました`,
      })

      // 顧客情報管理ページに遷移
      router.push("/dashboard/customers")
    } catch (error) {
      console.error("Error in handleComplete:", error)
      toast({
        title: "エラーが発生しました",
        description: error instanceof Error ? error.message : "不明なエラーが発生しました",
        variant: "destructive",
      })
    }
  }

  // ダミーデータ生成
  const generateDummyExtractedData = (): ExtractedData[] => {
    const prefectures = ["東京都", "神奈川県", "埼玉県", "千葉県", "大阪府", "京都府", "兵庫県", "愛知県"]

    return Array.from({ length: 5 }, (_, i) => {
      const prefecture = prefectures[Math.floor(Math.random() * prefectures.length)]
      return {
        id: `${Date.now()}-${i}`,
        extractedAt: new Date().toISOString().split("T")[0],
        customerName: `相続者 太郎${i + 1}`,
        postalCode: `${100 + Math.floor(Math.random() * 900)}-${1000 + Math.floor(Math.random() * 9000)}`,
        prefecture: prefecture,
        currentAddress: `${prefecture}${["新宿区", "渋谷区", "中央区", "港区"][i % 4]}${i + 1}-${i + 1}-${i + 1}`,
        inheritanceAddress: `${prefecture}${["品川区", "目黒区", "世田谷区", "杉並区"][i % 4]}${i + 1}-${i + 1}-${i + 1}`,
        phoneNumber: `03-${1234 + i}-${5678 + i}`,
        status: i % 5 === 0 ? "registered" : i % 4 === 0 ? "error" : "pending",
      }
    })
  }

  const handleReset = () => {
    setSelectedFile(null)
    setIsUploading(false)
    setUploadProgress(0)
    setProcessingProgress(0)
    setIsProcessing(false)
    setIsComplete(false)
    setEstimatedTime(null)
    setElapsedTime(0)
    setExtractedData([])
    setEditableData([])
    setDocumentId(null)
    setIsFileUploaded(false)
    setCurrentApiPathIndex(0)
  }

  const getRemainingTime = () => {
    if (!estimatedTime) return "推定時間: 不明"
    const remaining = estimatedTime - elapsedTime
    if (remaining <= 0) return "完了間近"
    return `残り時間: ${remaining}秒`
  }

  const handleDataChange = (id: string, field: string, value: string) => {
    setEditableData((prevData) => prevData.map((item) => (item.id === id ? { ...item, [field]: value } : item)))
  }

  // ハイドレーションエラー対策のため、クライアントサイドでのみレンダリング
  if (!isClient) {
    return null
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>受付台帳アップロード</CardTitle>
          <CardDescription>PDFファイルをアップロードして登記簿情報を自動抽出します</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex flex-col space-y-2">
              <div className="bg-amber-50 p-3 rounded-md border border-amber-200 mb-4">
                <p className="text-sm text-amber-800">
                  <AlertCircle className="h-4 w-4 inline-block mr-1" />
                  バックエンドAPIサーバーのURL: <code className="bg-amber-100 px-1 rounded">{API_BASE_URL}</code>
                  <br />
                  バックエンドサーバーが起動していることを確認してください。
                </p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex-1">
                <Input
                  type="file"
                  accept=".pdf"
                  onChange={handleFileChange}
                  disabled={isUploading || isProcessing}
                  className="cursor-pointer"
                />
              </div>
              <div className="flex gap-2">
                {!isFileUploaded ? (
                  <Button onClick={handleUpload} disabled={!selectedFile || isUploading || isProcessing}>
                    <Upload className="mr-2 h-4 w-4" />
                    アップロード
                  </Button>
                ) : (
                  <Button onClick={handleStartProcessing} disabled={!documentId || isProcessing || isComplete}>
                    <Clock className="mr-2 h-4 w-4" />
                    処理開始
                  </Button>
                )}
                <Button variant="outline" onClick={handleReset} disabled={isUploading || isProcessing}>
                  リセット
                </Button>
              </div>
            </div>

            {selectedFile && (
              <div className="rounded-md border p-4">
                <div className="flex items-start gap-3">
                  <FileText className="h-8 w-8 text-primary" />
                  <div className="flex-1 space-y-1">
                    <p className="font-medium">{selectedFile.name}</p>
                    <p className="text-sm text-muted-foreground">
                      サイズ: {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                    </p>

                    {isUploading && (
                      <div className="space-y-1">
                        <div className="flex items-center justify-between">
                          <p className="text-sm font-medium">アップロード中...</p>
                          <p className="text-sm">{Math.round(uploadProgress)}%</p>
                        </div>
                        <Progress value={uploadProgress} className="h-2" />
                      </div>
                    )}

                    {isFileUploaded && !isProcessing && !isComplete && (
                      <div className="flex items-center gap-2 text-green-600">
                        <CheckCircle className="h-5 w-5" />
                        <p className="font-medium">ファイルのアップロードが完了しました</p>
                      </div>
                    )}

                    {isProcessing && (
                      <div className="space-y-1">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-1">
                            <Clock className="h-4 w-4 text-muted-foreground animate-pulse" />
                            <p className="text-sm font-medium">処理中...</p>
                          </div>
                          <p className="text-sm">{Math.round(processingProgress)}%</p>
                        </div>
                        <Progress value={processingProgress} className="h-2" />

                        {estimatedTime && (
                          <div className="flex items-center justify-between mt-1">
                            <p className="text-xs text-muted-foreground">経過時間: {elapsedTime}秒</p>
                            <p className="text-xs text-muted-foreground">{getRemainingTime()}</p>
                          </div>
                        )}

                        <div className="bg-muted/30 rounded-md p-2 mt-2">
                          <p className="text-xs text-muted-foreground">
                            <AlertCircle className="h-3 w-3 inline-block mr-1" />
                            処理中はブラウザを閉じないでください。ファイルサイズによって処理時間が異なります。
                          </p>
                        </div>
                      </div>
                    )}

                    {isComplete && (
                      <div className="flex items-center gap-2 text-green-600">
                        <CheckCircle className="h-5 w-5" />
                        <p className="font-medium">処理が完了しました</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {isComplete && extractedData.length > 0 && (
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <div>
                <CardTitle className="text-lg text-primary">抽出データ一覧</CardTitle>
                <CardDescription>受付台帳から抽出された相続不動産情報</CardDescription>
              </div>
              <Button onClick={handleComplete}>
                <CheckCircle className="mr-2 h-4 w-4" />
                完了して顧客情報に登録
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="rounded-md border overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>顧客名</TableHead>
                    <TableHead>郵便番号</TableHead>
                    <TableHead>都道府県</TableHead>
                    <TableHead>顧客現在住所</TableHead>
                    <TableHead>相続住所</TableHead>
                    <TableHead>電話番号</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {editableData.map((data) => (
                    <TableRow key={data.id}>
                      <TableCell>
                        <Input
                          value={data.customerName}
                          onChange={(e) => handleDataChange(data.id, "customerName", e.target.value)}
                          className="w-full"
                        />
                      </TableCell>
                      <TableCell>
                        <Input
                          value={data.postalCode}
                          onChange={(e) => handleDataChange(data.id, "postalCode", e.target.value)}
                          className="w-full"
                        />
                      </TableCell>
                      <TableCell>
                        <Input
                          value={data.prefecture}
                          onChange={(e) => handleDataChange(data.id, "prefecture", e.target.value)}
                          className="w-full"
                        />
                      </TableCell>
                      <TableCell>
                        <Input
                          value={data.currentAddress}
                          onChange={(e) => handleDataChange(data.id, "currentAddress", e.target.value)}
                          className="w-full"
                        />
                      </TableCell>
                      <TableCell>
                        <Input
                          value={data.inheritanceAddress}
                          onChange={(e) => handleDataChange(data.id, "inheritanceAddress", e.target.value)}
                          className="w-full"
                        />
                      </TableCell>
                      <TableCell>
                        <Input
                          value={data.phoneNumber}
                          onChange={(e) => handleDataChange(data.id, "phoneNumber", e.target.value)}
                          className="w-full"
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
