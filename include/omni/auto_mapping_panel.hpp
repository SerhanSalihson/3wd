#ifndef OMNI__AUTO_MAPPING_PANEL_HPP_
#define OMNI__AUTO_MAPPING_PANEL_HPP_

#include <QProcess>

#include "rviz_common/panel.hpp"

class QLabel;
class QPushButton;

namespace omni
{

class AutoMappingPanel : public rviz_common::Panel
{
  Q_OBJECT

public:
  explicit AutoMappingPanel(QWidget * parent = nullptr);
  ~AutoMappingPanel() override;

private Q_SLOTS:
  void startMapping();
  void stopMapping();
  void processStarted();
  void processFinished(int exit_code, QProcess::ExitStatus exit_status);
  void processError(QProcess::ProcessError error);

private:
  void setRunning(bool running);
  void setStatus(const QString & text, const QString & color);

  QProcess * mapper_process_;
  QPushButton * start_button_;
  QPushButton * stop_button_;
  QLabel * status_label_;
  bool stop_requested_;
};

}  // namespace omni

#endif  // OMNI__AUTO_MAPPING_PANEL_HPP_
